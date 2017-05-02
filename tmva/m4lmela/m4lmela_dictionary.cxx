// Do NOT change. Changes will be lost next time file is generated

#define R__DICTIONARY_FILENAME m4lmela_dictionary

/*******************************************************************/
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#define G__DICTIONARY
#include "RConfig.h"
#include "TClass.h"
#include "TDictAttributeMap.h"
#include "TInterpreter.h"
#include "TROOT.h"
#include "TBuffer.h"
#include "TMemberInspector.h"
#include "TInterpreter.h"
#include "TVirtualMutex.h"
#include "TError.h"

#ifndef G__ROOT
#define G__ROOT
#endif

#include "RtypesImp.h"
#include "TIsAProxy.h"
#include "TFileMergeInfo.h"
#include <algorithm>
#include "TCollectionProxyInfo.h"
/*******************************************************************/

#include "TDataMember.h"

// Since CINT ignores the std namespace, we need to do so in this file.
namespace std {} using namespace std;

// Header files passed as explicit arguments
#include "m4lmela.cc"

// Header files passed via #pragma extra_include

namespace ROOT {
   static TClass *pairlEdoublecOstringgR_Dictionary();
   static void pairlEdoublecOstringgR_TClassManip(TClass*);
   static void *new_pairlEdoublecOstringgR(void *p = 0);
   static void *newArray_pairlEdoublecOstringgR(Long_t size, void *p);
   static void delete_pairlEdoublecOstringgR(void *p);
   static void deleteArray_pairlEdoublecOstringgR(void *p);
   static void destruct_pairlEdoublecOstringgR(void *p);

   // Function generating the singleton type initializer
   static TGenericClassInfo *GenerateInitInstanceLocal(const pair<double,string>*)
   {
      pair<double,string> *ptr = 0;
      static ::TVirtualIsAProxy* isa_proxy = new ::TIsAProxy(typeid(pair<double,string>));
      static ::ROOT::TGenericClassInfo 
         instance("pair<double,string>", "utility", 253,
                  typeid(pair<double,string>), ::ROOT::Internal::DefineBehavior(ptr, ptr),
                  &pairlEdoublecOstringgR_Dictionary, isa_proxy, 4,
                  sizeof(pair<double,string>) );
      instance.SetNew(&new_pairlEdoublecOstringgR);
      instance.SetNewArray(&newArray_pairlEdoublecOstringgR);
      instance.SetDelete(&delete_pairlEdoublecOstringgR);
      instance.SetDeleteArray(&deleteArray_pairlEdoublecOstringgR);
      instance.SetDestructor(&destruct_pairlEdoublecOstringgR);

      ::ROOT::AddClassAlternate("pair<double,string>","pair<double,std::string>");
      return &instance;
   }
   // Static variable to force the class initialization
   static ::ROOT::TGenericClassInfo *_R__UNIQUE_(Init) = GenerateInitInstanceLocal((const pair<double,string>*)0x0); R__UseDummy(_R__UNIQUE_(Init));

   // Dictionary for non-ClassDef classes
   static TClass *pairlEdoublecOstringgR_Dictionary() {
      TClass* theClass =::ROOT::GenerateInitInstanceLocal((const pair<double,string>*)0x0)->GetClass();
      pairlEdoublecOstringgR_TClassManip(theClass);
   return theClass;
   }

   static void pairlEdoublecOstringgR_TClassManip(TClass* ){
   }

} // end of namespace ROOT

namespace ROOT {
   static TClass *__m4lmelacLcLReadMLP_Dictionary();
   static void __m4lmelacLcLReadMLP_TClassManip(TClass*);
   static void delete___m4lmelacLcLReadMLP(void *p);
   static void deleteArray___m4lmelacLcLReadMLP(void *p);
   static void destruct___m4lmelacLcLReadMLP(void *p);

   // Function generating the singleton type initializer
   static TGenericClassInfo *GenerateInitInstanceLocal(const ::__m4lmela::ReadMLP*)
   {
      ::__m4lmela::ReadMLP *ptr = 0;
      static ::TVirtualIsAProxy* isa_proxy = new ::TIsAProxy(typeid(::__m4lmela::ReadMLP));
      static ::ROOT::TGenericClassInfo 
         instance("__m4lmela::ReadMLP", "m4lmela.cc", 125,
                  typeid(::__m4lmela::ReadMLP), ::ROOT::Internal::DefineBehavior(ptr, ptr),
                  &__m4lmelacLcLReadMLP_Dictionary, isa_proxy, 4,
                  sizeof(::__m4lmela::ReadMLP) );
      instance.SetDelete(&delete___m4lmelacLcLReadMLP);
      instance.SetDeleteArray(&deleteArray___m4lmelacLcLReadMLP);
      instance.SetDestructor(&destruct___m4lmelacLcLReadMLP);
      return &instance;
   }
   TGenericClassInfo *GenerateInitInstance(const ::__m4lmela::ReadMLP*)
   {
      return GenerateInitInstanceLocal((::__m4lmela::ReadMLP*)0);
   }
   // Static variable to force the class initialization
   static ::ROOT::TGenericClassInfo *_R__UNIQUE_(Init) = GenerateInitInstanceLocal((const ::__m4lmela::ReadMLP*)0x0); R__UseDummy(_R__UNIQUE_(Init));

   // Dictionary for non-ClassDef classes
   static TClass *__m4lmelacLcLReadMLP_Dictionary() {
      TClass* theClass =::ROOT::GenerateInitInstanceLocal((const ::__m4lmela::ReadMLP*)0x0)->GetClass();
      __m4lmelacLcLReadMLP_TClassManip(theClass);
   return theClass;
   }

   static void __m4lmelacLcLReadMLP_TClassManip(TClass* ){
   }

} // end of namespace ROOT

namespace ROOT {
   static TClass *m4lmela_Dictionary();
   static void m4lmela_TClassManip(TClass*);
   static void *new_m4lmela(void *p = 0);
   static void *newArray_m4lmela(Long_t size, void *p);
   static void delete_m4lmela(void *p);
   static void deleteArray_m4lmela(void *p);
   static void destruct_m4lmela(void *p);

   // Function generating the singleton type initializer
   static TGenericClassInfo *GenerateInitInstanceLocal(const ::m4lmela*)
   {
      ::m4lmela *ptr = 0;
      static ::TVirtualIsAProxy* isa_proxy = new ::TIsAProxy(typeid(::m4lmela));
      static ::ROOT::TGenericClassInfo 
         instance("m4lmela", "m4lmela.cc", 466,
                  typeid(::m4lmela), ::ROOT::Internal::DefineBehavior(ptr, ptr),
                  &m4lmela_Dictionary, isa_proxy, 4,
                  sizeof(::m4lmela) );
      instance.SetNew(&new_m4lmela);
      instance.SetNewArray(&newArray_m4lmela);
      instance.SetDelete(&delete_m4lmela);
      instance.SetDeleteArray(&deleteArray_m4lmela);
      instance.SetDestructor(&destruct_m4lmela);
      return &instance;
   }
   TGenericClassInfo *GenerateInitInstance(const ::m4lmela*)
   {
      return GenerateInitInstanceLocal((::m4lmela*)0);
   }
   // Static variable to force the class initialization
   static ::ROOT::TGenericClassInfo *_R__UNIQUE_(Init) = GenerateInitInstanceLocal((const ::m4lmela*)0x0); R__UseDummy(_R__UNIQUE_(Init));

   // Dictionary for non-ClassDef classes
   static TClass *m4lmela_Dictionary() {
      TClass* theClass =::ROOT::GenerateInitInstanceLocal((const ::m4lmela*)0x0)->GetClass();
      m4lmela_TClassManip(theClass);
   return theClass;
   }

   static void m4lmela_TClassManip(TClass* ){
   }

} // end of namespace ROOT

namespace ROOT {
   // Wrappers around operator new
   static void *new_pairlEdoublecOstringgR(void *p) {
      return  p ? ::new((::ROOT::Internal::TOperatorNewHelper*)p) pair<double,string> : new pair<double,string>;
   }
   static void *newArray_pairlEdoublecOstringgR(Long_t nElements, void *p) {
      return p ? ::new((::ROOT::Internal::TOperatorNewHelper*)p) pair<double,string>[nElements] : new pair<double,string>[nElements];
   }
   // Wrapper around operator delete
   static void delete_pairlEdoublecOstringgR(void *p) {
      delete ((pair<double,string>*)p);
   }
   static void deleteArray_pairlEdoublecOstringgR(void *p) {
      delete [] ((pair<double,string>*)p);
   }
   static void destruct_pairlEdoublecOstringgR(void *p) {
      typedef pair<double,string> current_t;
      ((current_t*)p)->~current_t();
   }
} // end of namespace ROOT for class pair<double,string>

namespace ROOT {
   // Wrapper around operator delete
   static void delete___m4lmelacLcLReadMLP(void *p) {
      delete ((::__m4lmela::ReadMLP*)p);
   }
   static void deleteArray___m4lmelacLcLReadMLP(void *p) {
      delete [] ((::__m4lmela::ReadMLP*)p);
   }
   static void destruct___m4lmelacLcLReadMLP(void *p) {
      typedef ::__m4lmela::ReadMLP current_t;
      ((current_t*)p)->~current_t();
   }
} // end of namespace ROOT for class ::__m4lmela::ReadMLP

namespace ROOT {
   // Wrappers around operator new
   static void *new_m4lmela(void *p) {
      return  p ? new(p) ::m4lmela : new ::m4lmela;
   }
   static void *newArray_m4lmela(Long_t nElements, void *p) {
      return p ? new(p) ::m4lmela[nElements] : new ::m4lmela[nElements];
   }
   // Wrapper around operator delete
   static void delete_m4lmela(void *p) {
      delete ((::m4lmela*)p);
   }
   static void deleteArray_m4lmela(void *p) {
      delete [] ((::m4lmela*)p);
   }
   static void destruct_m4lmela(void *p) {
      typedef ::m4lmela current_t;
      ((current_t*)p)->~current_t();
   }
} // end of namespace ROOT for class ::m4lmela

namespace ROOT {
   static TClass *vectorlEstringgR_Dictionary();
   static void vectorlEstringgR_TClassManip(TClass*);
   static void *new_vectorlEstringgR(void *p = 0);
   static void *newArray_vectorlEstringgR(Long_t size, void *p);
   static void delete_vectorlEstringgR(void *p);
   static void deleteArray_vectorlEstringgR(void *p);
   static void destruct_vectorlEstringgR(void *p);

   // Function generating the singleton type initializer
   static TGenericClassInfo *GenerateInitInstanceLocal(const vector<string>*)
   {
      vector<string> *ptr = 0;
      static ::TVirtualIsAProxy* isa_proxy = new ::TIsAProxy(typeid(vector<string>));
      static ::ROOT::TGenericClassInfo 
         instance("vector<string>", -2, "vector", 458,
                  typeid(vector<string>), ::ROOT::Internal::DefineBehavior(ptr, ptr),
                  &vectorlEstringgR_Dictionary, isa_proxy, 0,
                  sizeof(vector<string>) );
      instance.SetNew(&new_vectorlEstringgR);
      instance.SetNewArray(&newArray_vectorlEstringgR);
      instance.SetDelete(&delete_vectorlEstringgR);
      instance.SetDeleteArray(&deleteArray_vectorlEstringgR);
      instance.SetDestructor(&destruct_vectorlEstringgR);
      instance.AdoptCollectionProxyInfo(TCollectionProxyInfo::Generate(TCollectionProxyInfo::Pushback< vector<string> >()));
      return &instance;
   }
   // Static variable to force the class initialization
   static ::ROOT::TGenericClassInfo *_R__UNIQUE_(Init) = GenerateInitInstanceLocal((const vector<string>*)0x0); R__UseDummy(_R__UNIQUE_(Init));

   // Dictionary for non-ClassDef classes
   static TClass *vectorlEstringgR_Dictionary() {
      TClass* theClass =::ROOT::GenerateInitInstanceLocal((const vector<string>*)0x0)->GetClass();
      vectorlEstringgR_TClassManip(theClass);
   return theClass;
   }

   static void vectorlEstringgR_TClassManip(TClass* ){
   }

} // end of namespace ROOT

namespace ROOT {
   // Wrappers around operator new
   static void *new_vectorlEstringgR(void *p) {
      return  p ? ::new((::ROOT::Internal::TOperatorNewHelper*)p) vector<string> : new vector<string>;
   }
   static void *newArray_vectorlEstringgR(Long_t nElements, void *p) {
      return p ? ::new((::ROOT::Internal::TOperatorNewHelper*)p) vector<string>[nElements] : new vector<string>[nElements];
   }
   // Wrapper around operator delete
   static void delete_vectorlEstringgR(void *p) {
      delete ((vector<string>*)p);
   }
   static void deleteArray_vectorlEstringgR(void *p) {
      delete [] ((vector<string>*)p);
   }
   static void destruct_vectorlEstringgR(void *p) {
      typedef vector<string> current_t;
      ((current_t*)p)->~current_t();
   }
} // end of namespace ROOT for class vector<string>

namespace ROOT {
   static TClass *vectorlEpairlEdoublecOstringgRsPgR_Dictionary();
   static void vectorlEpairlEdoublecOstringgRsPgR_TClassManip(TClass*);
   static void *new_vectorlEpairlEdoublecOstringgRsPgR(void *p = 0);
   static void *newArray_vectorlEpairlEdoublecOstringgRsPgR(Long_t size, void *p);
   static void delete_vectorlEpairlEdoublecOstringgRsPgR(void *p);
   static void deleteArray_vectorlEpairlEdoublecOstringgRsPgR(void *p);
   static void destruct_vectorlEpairlEdoublecOstringgRsPgR(void *p);

   // Function generating the singleton type initializer
   static TGenericClassInfo *GenerateInitInstanceLocal(const vector<pair<double,string> >*)
   {
      vector<pair<double,string> > *ptr = 0;
      static ::TVirtualIsAProxy* isa_proxy = new ::TIsAProxy(typeid(vector<pair<double,string> >));
      static ::ROOT::TGenericClassInfo 
         instance("vector<pair<double,string> >", -2, "vector", 458,
                  typeid(vector<pair<double,string> >), ::ROOT::Internal::DefineBehavior(ptr, ptr),
                  &vectorlEpairlEdoublecOstringgRsPgR_Dictionary, isa_proxy, 4,
                  sizeof(vector<pair<double,string> >) );
      instance.SetNew(&new_vectorlEpairlEdoublecOstringgRsPgR);
      instance.SetNewArray(&newArray_vectorlEpairlEdoublecOstringgRsPgR);
      instance.SetDelete(&delete_vectorlEpairlEdoublecOstringgRsPgR);
      instance.SetDeleteArray(&deleteArray_vectorlEpairlEdoublecOstringgRsPgR);
      instance.SetDestructor(&destruct_vectorlEpairlEdoublecOstringgRsPgR);
      instance.AdoptCollectionProxyInfo(TCollectionProxyInfo::Generate(TCollectionProxyInfo::Pushback< vector<pair<double,string> > >()));
      return &instance;
   }
   // Static variable to force the class initialization
   static ::ROOT::TGenericClassInfo *_R__UNIQUE_(Init) = GenerateInitInstanceLocal((const vector<pair<double,string> >*)0x0); R__UseDummy(_R__UNIQUE_(Init));

   // Dictionary for non-ClassDef classes
   static TClass *vectorlEpairlEdoublecOstringgRsPgR_Dictionary() {
      TClass* theClass =::ROOT::GenerateInitInstanceLocal((const vector<pair<double,string> >*)0x0)->GetClass();
      vectorlEpairlEdoublecOstringgRsPgR_TClassManip(theClass);
   return theClass;
   }

   static void vectorlEpairlEdoublecOstringgRsPgR_TClassManip(TClass* ){
   }

} // end of namespace ROOT

namespace ROOT {
   // Wrappers around operator new
   static void *new_vectorlEpairlEdoublecOstringgRsPgR(void *p) {
      return  p ? ::new((::ROOT::Internal::TOperatorNewHelper*)p) vector<pair<double,string> > : new vector<pair<double,string> >;
   }
   static void *newArray_vectorlEpairlEdoublecOstringgRsPgR(Long_t nElements, void *p) {
      return p ? ::new((::ROOT::Internal::TOperatorNewHelper*)p) vector<pair<double,string> >[nElements] : new vector<pair<double,string> >[nElements];
   }
   // Wrapper around operator delete
   static void delete_vectorlEpairlEdoublecOstringgRsPgR(void *p) {
      delete ((vector<pair<double,string> >*)p);
   }
   static void deleteArray_vectorlEpairlEdoublecOstringgRsPgR(void *p) {
      delete [] ((vector<pair<double,string> >*)p);
   }
   static void destruct_vectorlEpairlEdoublecOstringgRsPgR(void *p) {
      typedef vector<pair<double,string> > current_t;
      ((current_t*)p)->~current_t();
   }
} // end of namespace ROOT for class vector<pair<double,string> >

namespace {
  void TriggerDictionaryInitialization_m4lmela_dictionary_Impl() {
    static const char* headers[] = {
"m4lmela.cc",
0
    };
    static const char* includePaths[] = {
"/Users/harry/external/root-6.08.04/include",
"/Users/harry/external/root-6.08.04/include",
"/Users/harry/Projects/Higgs/monoHZZ4L/Run2016/tmva/m4lmela/",
0
    };
    static const char* fwdDeclCode = R"DICTFWDDCLS(
#line 1 "m4lmela_dictionary dictionary forward declarations' payload"
#pragma clang diagnostic ignored "-Wkeyword-compat"
#pragma clang diagnostic ignored "-Wignored-attributes"
#pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
extern int __Cling_Autoloading_Map;
namespace std{inline namespace __1{template <class _CharT> struct __attribute__((annotate("$clingAutoload$string")))  char_traits;
}}
namespace std{inline namespace __1{template <class _Tp> class __attribute__((annotate("$clingAutoload$iosfwd")))  __attribute__((annotate("$clingAutoload$string")))  allocator;
}}
namespace __m4lmela{class __attribute__((annotate("$clingAutoload$m4lmela.cc")))  ReadMLP;}
struct __attribute__((annotate("$clingAutoload$m4lmela.cc")))  m4lmela;
)DICTFWDDCLS";
    static const char* payloadCode = R"DICTPAYLOAD(
#line 1 "m4lmela_dictionary dictionary payload"

#ifndef G__VECTOR_HAS_CLASS_ITERATOR
  #define G__VECTOR_HAS_CLASS_ITERATOR 1
#endif

#define _BACKWARD_BACKWARD_WARNING_H
#include "m4lmela.cc"

#undef  _BACKWARD_BACKWARD_WARNING_H
)DICTPAYLOAD";
    static const char* classesHeaders[]={
"__m4lmela::ReadMLP", payloadCode, "@",
"m4lmela", payloadCode, "@",
nullptr};

    static bool isInitialized = false;
    if (!isInitialized) {
      TROOT::RegisterModule("m4lmela_dictionary",
        headers, includePaths, payloadCode, fwdDeclCode,
        TriggerDictionaryInitialization_m4lmela_dictionary_Impl, {}, classesHeaders);
      isInitialized = true;
    }
  }
  static struct DictInit {
    DictInit() {
      TriggerDictionaryInitialization_m4lmela_dictionary_Impl();
    }
  } __TheDictionaryInitializer;
}
void TriggerDictionaryInitialization_m4lmela_dictionary() {
  TriggerDictionaryInitialization_m4lmela_dictionary_Impl();
}
