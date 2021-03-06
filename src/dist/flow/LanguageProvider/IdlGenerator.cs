﻿/*
 * The MIT License (MIT)
 *
 * Copyright (c) 2015 Microsoft Corporation
 * 
 * -=- Robust Distributed System Nucleus (rDSN) -=- 
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

/*
 * Description:
 *     What is this file about?
 *
 * Revision history:
 *     Feb., 2016, @imzhenyu (Zhenyu Guo), done in Tron project and copied here
 *     xxxx-xx-xx, author, fix bug about xxx
 */

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using IDL;
using rDSN.Tron.Utility;

namespace rDSN.Tron.LanguageProvider
{
    public abstract class IdlGenerator
    {
        // TODO: change public to protected
        public abstract void GenerateHeader();
        public abstract void GenerateEnums();
        public abstract void GenerateStructs();
        public abstract void GenerateApis();

        public virtual void Generate(Assembly asm, CodeBuilder c)
        {
            this.asm = asm;
            this.c = c;
            GenerateHeader();
            GenerateEnums();
            GenerateStructs();
            GenerateApis();
        }

        public virtual void Generate(Assembly asm)
        {
            this.asm = asm;
            c = new CodeBuilder();
            GenerateHeader();
            GenerateEnums();
            GenerateStructs();
            GenerateApis();
        }

        public override string ToString()
        {
            return c.ToString();
        }


        public static IdlGenerator GetInstance(string name)
        {
            switch (name)
            {
                case "proto":
                    return new ProtoGenerator();
                case "thrift":
                    return new ThriftGenerator();
                default:
                    return null;
            }
        }

        public static IdlGenerator GetInstance(ServiceSpecType t)
        {
            switch (t)
            {
                case ServiceSpecType.Proto:
                    return new ProtoGenerator();
                case ServiceSpecType.Thrift:
                    return new ThriftGenerator();
                default:
                    return null;
            }
        }

        protected List<string> FindDependency(Type t)
        {
            var fields = t.GetFields().ToList();
            var res = new List<string>();
            foreach (var field in fields)
            {
                res.AddRange(GetUserTypes(field.FieldType));
            }

            return res.Distinct().Where(d => d != t.Name).ToList();
        }

        protected List<string> GetUserTypes(Type t)
        {
            var res = new List<string>();
            if (t.IsGenericType)
            {
                foreach (var subField in t.GenericTypeArguments)
                {
                    res.AddRange(GetUserTypes(subField));
                }
            }
            else if (!t.Namespace.StartsWith("System") && !t.IsEnum)
            {
                res.Add(t.Name);
            }
            return res;
        }

        /// <summary>
        /// In case some structs have dependency problems
        /// e.g., does not support forward type search.
        /// Sort the type list according to their dependency relationships
        /// </summary>
        protected void SortTypeByDependency(ref List<Type> structs)
        {
            var names = structs.Select(a => a.Name);
            var flag = new Dictionary<string, bool>();
            foreach (var name in names)
            {
                flag[name] = false;
            }
            for (var i = 0; i < structs.Count; )
            {
                var dependencyList = FindDependency(structs[i]);
                if (dependencyList.Any())
                {
                    foreach (var name in dependencyList.Where(name => flag[name] == false))
                    {
                        var pos = structs.FindIndex(s => s.Name == name);
                        var tmp = structs[i];
                        structs[i] = structs[pos];
                        structs[pos] = tmp;
                        break;
                    }
                    if (dependencyList.Count(t => flag[t] == false) != 0) continue;
                    flag[structs[i].Name] = true;
                    i++;
                }
                else
                {
                    flag[structs[i].Name] = true;
                    i++;
                }
            }

        }

        protected Assembly asm;
        protected CodeBuilder c;
        protected abstract string CastToIdlType(Type t);

        public string name = "";
        public bool supportForwardSearch;
        public bool supportNested;

    }

    public class ProtoGenerator : IdlGenerator
    {
        public ProtoGenerator()
        {
            name = "proto";
            supportForwardSearch = true;
            supportNested = true;
        }

        public override void GenerateHeader()
        {
            var nspace = asm.GetTypes().Select(t => t.Namespace).Distinct().First();
            c.AppendLine("package " + nspace + ";");
            c.AppendLine();
        }
        public override void GenerateEnums()
        {
            var enums = asm.GetExportedTypes().Where(t => t.IsEnum);
            foreach (var e in enums)
            {
                c.AppendLine("enum " + e.Name);
                c.BeginBlock();
                var fields = e.GetFields().ToList();
                fields.RemoveAt(0);
                foreach (var member in fields)
                {
                    var defaultValue = "";
                    var fieldAttribute = member.GetCustomAttribute(typeof(FieldAttribute)) as FieldAttribute;
                    if (fieldAttribute.DefaultValue != null)
                    {
                        defaultValue = " = " + fieldAttribute.DefaultValue;
                    }
                    c.AppendLine(member.Name + defaultValue + ";");
                }
                c.EndBlock();
                c.AppendLine();
            }


        }

        public override void GenerateStructs()
        {
            // class is allowed here to support inheritance
            // if we don't want to support class definition in C#, just delete the "t.IsClass"
            var structs = asm.GetExportedTypes().Where(t => (t.IsValueType || t.IsClass) && !t.IsEnum).ToList();
            if (!supportForwardSearch)
            {
                SortTypeByDependency(ref structs);
            }

            foreach (var s in structs)
            {
                var fields = s.GetFields().ToList();
                if (s.BaseType.Namespace != "System") // has parent class
                {
                    c.AppendLine("message " + s.Name + " : " + s.BaseType.Name);
                    var baseFields = s.BaseType.GetFields();
                    fields = fields.Where(f => baseFields.Count(bf => bf.Name == f.Name) == 0).ToList();
                }
                else
                {
                    c.AppendLine("message " + s.Name);
                }

                c.BeginBlock();
                var lineNumber = 0;
                foreach (var member in fields)
                {
                    var modifier = "";
                    var defaultValue = ";";
                    var fieldAttribute = member.GetCustomAttribute(typeof(FieldAttribute)) as FieldAttribute;
                    if (fieldAttribute != null)
                    {
                        lineNumber = fieldAttribute.Index;
                        modifier = fieldAttribute.Modifier;// == "optional" ? "" : fieldAttribute.modifier;
                        defaultValue = fieldAttribute.DefaultValue;
                        if (defaultValue != null)
                        {
                            defaultValue = " [default = " + defaultValue + "];";
                        }
                        else
                        {
                            defaultValue = ";";
                        }

                    }

                    c.AppendLine(modifier + " " + CastToIdlType(member.FieldType) + " " + member.Name + " = " + lineNumber + defaultValue);


                }
                c.EndBlock();
                c.AppendLine();
            }

        }

        public override void GenerateApis()
        {
            var structs = asm.GetExportedTypes().Where(t => t.IsInterface && t.IsPublic);     // select the interface types
            foreach (var s in structs)
            {
                var serviceMethods = s.GetMethods().ToList();
                foreach (var parent in s.GetInterfaces())  // parent interface's methods
                {
                    serviceMethods.AddRange(parent.GetMethods());
                }

                c.AppendLine("service " + s.Name);
                c.BeginBlock();
                foreach (var method in serviceMethods)
                {
                    var paramList = method.GetParameters().Select(p => CastToIdlType(p.ParameterType) + " " + p.Name);
                    if (paramList.Count() > 1)
                    {
                        Console.WriteLine("Error: Only one parameter is supported by service definition...");
                    }

                    c.AppendLine("rpc " + method.Name + " (" + string.Join(", ", paramList) + ") returns (" + CastToIdlType(method.ReturnType) + ");");
                    Console.WriteLine();
                }
                c.EndBlock();
                c.AppendLine();
            }

        }

        /// <summary>
        /// Cast the C# Type to IDL Type
        /// Do not take the prefix.
        /// </summary>
        /// <example>
        ///     system.int32        =>      int32
        ///     system.Double       =>      double
        ///     system.string       =>      string
        ///     namespace.typename  =>      typename
        ///     composite type      =>      simplified type, no prefix
        /// </example>
        /// <param name="s">C# code type</param>
        /// <returns>mapped IDL type string</returns>
        protected override string CastToIdlType(Type s)
        {
            if (!s.Namespace.StartsWith("System"))
            {
                return s.Name;
            }
            if (s.IsGenericType)
            {
                var genericTypeName = IdlTypeMaps[s.Name.Split('`').First()];
                var genericParamList = s.GenericTypeArguments.Select(CastToIdlType);
                return genericTypeName + "<" + string.Join(", ", genericParamList) + ">";
            }
            if (IdlTypeMaps.ContainsKey(s.Name))
            {
                return IdlTypeMaps[s.Name];
            }
            return s.Name.ToLower();
        }

        #region private fields
        private Dictionary<string, string> IdlTypeMaps = new Dictionary<string, string>
        {
            // generic types
            {"List"         , "vector"},
            {"Dictionary"   , "map"},

            // system types
            {"Boolean"      , "bool"},
            {"Char"         , "string"},
            {"Decimal"      , "double"},
            {"Double"       , "double"},
            {"Single"       , "float"},
            {"Int16"        , "int16"},
            {"UInt16"       , "uint16"},
            {"Int32"        , "int32"},
            {"UInt32"       , "uint32"},
            {"Int64"        , "int64"},
            {"UInt64"       , "uint64"}
            //{"Object"       , "object"}       // do not support object？
             //{"Byte"         , "byte"},        // do not support byte?
            //{"SByte"        , "sbyte"},
            
        };
        #endregion


    }

    public class ThriftGenerator : IdlGenerator
    {
        public ThriftGenerator()
        {
            name = "thrift";
            supportForwardSearch = true;
            supportNested = true;
        }

        public override void GenerateHeader()
        {
            var nspace = asm.GetTypes().Select(t => t.Namespace).Distinct().First();
            c.AppendLine("package " + nspace + ";");
            c.AppendLine();
        }
        public override void GenerateEnums()
        {
            var enums = asm.GetExportedTypes().Where(t => t.IsEnum);
            foreach (var e in enums)
            {
                c.AppendLine("enum " + e.Name);
                c.BeginBlock();
                var fields = e.GetFields().ToList();
                fields.RemoveAt(0);
                foreach (var member in fields)
                {
                    var defaultValue = "";
                    var fieldAttribute = member.GetCustomAttribute(typeof(FieldAttribute)) as FieldAttribute;
                    if (fieldAttribute.DefaultValue != null)
                    {
                        defaultValue = " = " + fieldAttribute.DefaultValue;
                    }
                    c.AppendLine(member.Name + defaultValue + ";");
                }
                c.EndBlock();
                c.AppendLine();
            }


        }

        public override void GenerateStructs()
        {
            // class is allowed here to support inheritance in IDL
            // if we don't want to support class definition in C#, just delete the "t.IsClass"
            var structs = asm.GetExportedTypes().Where(t => (t.IsValueType || t.IsClass) && !t.IsEnum).ToList();
            if (!supportForwardSearch)
            {
                SortTypeByDependency(ref structs);
            }

            foreach (var s in structs)
            {
                var fields = s.GetFields().ToList();
                if (s.BaseType.Namespace != "System") // has parent class
                {
                    c.AppendLine("message " + s.Name + " : " + s.BaseType.Name);
                    var baseFields = s.BaseType.GetFields();
                    fields = fields.Where(f => baseFields.Count(bf => bf.Name == f.Name) == 0).ToList();
                }
                else
                {
                    c.AppendLine("message " + s.Name);
                }

                c.BeginBlock();
                var lineNumber = 0;
                foreach (var member in fields)
                {
                    var modifier = "";
                    var defaultValue = ";";
                    var fieldAttribute = member.GetCustomAttribute(typeof(FieldAttribute)) as FieldAttribute;
                    if (fieldAttribute != null)
                    {
                        lineNumber = fieldAttribute.Index;
                        modifier = fieldAttribute.Modifier;// == "optional" ? "" : fieldAttribute.modifier;
                        defaultValue = fieldAttribute.DefaultValue;
                        if (defaultValue != null)
                        {
                            defaultValue = " [default = " + defaultValue + "];";
                        }
                        else
                        {
                            defaultValue = ";";
                        }

                    }

                    c.AppendLine(modifier + " " + CastToIdlType(member.FieldType) + " " + member.Name + " = " + lineNumber + defaultValue);


                }
                c.EndBlock();
                c.AppendLine();
            }

        }

        public override void GenerateApis()
        {
            var structs = asm.GetExportedTypes().Where(t => t.IsInterface && t.IsPublic);     // select the interface types
            foreach (var s in structs)
            {
                var serviceMethods = s.GetMethods().ToList();
                foreach (var parent in s.GetInterfaces())  // parent interface's methods
                {
                    serviceMethods.AddRange(parent.GetMethods());
                }

                c.AppendLine("service " + s.Name);
                c.BeginBlock();
                foreach (var method in serviceMethods)
                {
                    var paramList = method.GetParameters().Select(p => CastToIdlType(p.ParameterType) + " " + p.Name);
                    if (paramList.Count() > 1)
                    {
                        Console.WriteLine("Error: Only one parameter is supported by IDL service definition...");
                    }

                    c.AppendLine("rpc " + method.Name + " (" + string.Join(", ", paramList) + ") returns (" + CastToIdlType(method.ReturnType) + ");");
                    Console.WriteLine();
                }
                c.EndBlock();
                c.AppendLine();
            }

        }

        /// <summary>
        /// Cast the C# Type to IDL Type
        /// Do not take the prefix.
        /// </summary>
        /// <example>
        ///     system.int32        =>      int32
        ///     system.Double       =>      double
        ///     system.string       =>      string
        ///     namespace.typename  =>      typename
        ///     composite type      =>      simplified type, no prefix
        /// </example>
        /// <param name="s">C# code type</param>
        /// <returns>mapped IDL type string</returns>
        protected override string CastToIdlType(Type s)
        {
            if (!s.Namespace.StartsWith("System"))
            {
                return s.Name;
            }
            if (s.IsGenericType)
            {
                var genericTypeName = IdlTypeMaps[s.Name.Split('`').First()];
                var genericParamList = s.GenericTypeArguments.Select(CastToIdlType);
                return genericTypeName + "<" + string.Join(", ", genericParamList) + ">";
            }
            if (IdlTypeMaps.ContainsKey(s.Name))
            {
                return IdlTypeMaps[s.Name];
            }
            return s.Name.ToLower();
        }

        #region private fields
        private Dictionary<string, string> IdlTypeMaps = new Dictionary<string, string>
        {
            // generic types
            {"List"         , "list"},
            {"Dictionary"   , "map"},
            {"Set", "set"}, 

            // system types
            {"Boolean"      , "bool"},
            {"Char"         , "string"},
            {"Decimal"      , "double"},
            {"Double"       , "double"},
            {"Single"       , "float"},
            {"Int16"        , "int16"},
            {"UInt16"       , "uint16"},
            {"Int32"        , "int32"},
            {"UInt32"       , "uint32"},
            {"Int64"        , "int64"},
            {"UInt64"       , "uint64"}
            //{"Object"       , "object"}       // do not support object？
             //{"Byte"         , "byte"},        // do not support byte?
            //{"SByte"        , "sbyte"},
            
        };
        #endregion


    }


    
}
