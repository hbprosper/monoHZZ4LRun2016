# ----------------------------------------------------------------------------
# Build libMVD.so
# Created 04-Jun-2017 HBP
# ----------------------------------------------------------------------------
ifndef ROOTSYS
	$(error *** Please set up Root)
endif
ROOFIT	:= $(ROOTSYS)
# ----------------------------------------------------------------------------
NAME	:= MVD
incdir	:= include
srcdir	:= src
libdir	:= lib


# create lib directory if one does not exist
$(shell mkdir -p lib)

# get lists of sources for which dicttionaries are needed
CPPSRCS	:= $(wildcard $(srcdir)/*.cpp)

CINTSRCS:= $(wildcard $(srcdir)/*_dict.cc)

OTHERSRCS:= $(filter-out $(CINTSRCS),$(wildcard $(srcdir)/*.cc))

# list of dictionaries to be created
DICTIONARIES	:= $(CPPSRCS:.cpp=_dict.cc)

# get list of objects
OBJECTS		:= $(OTHERSRCS:.cc=.o) $(DICTIONARIES:.cc=.o)
#say := $(shell echo "DICTIONARIES:     $(DICTIONARIES)" >& 2)

LINKDEF	:= $(srcdir)/linkdef.h

# ----------------------------------------------------------------------------
ROOTCINT	:= rootcint
# check for clang++, otherwise use g++
COMPILER	:= $(shell which clang++)
ifneq ($(COMPILER),)
CXX		:= clang++
LD		:= clang++
else
CXX		:= g++
LD		:= g++
endif

CPPFLAGS	:= -I. -I$(incdir)
CXXFLAGS	:= -O3 -Wall -fPIC -g -ansi -Wshadow -Wextra \
$(shell root-config --cflags)
LDFLAGS		:= -g
# ----------------------------------------------------------------------------
# which operating system?
OS := $(shell uname -s)
ifeq ($(OS),Darwin)
	LDFLAGS += -dynamiclib
	LDEXT	:= .dylib
else
	LDFLAGS	+= -shared
	LDEXT	:= .so
endif
LDFLAGS += $(shell root-config --ldflags)
LIBS	:= $(shell root-config --libs) -lTreePlayer -lPyROOT
LIBRARY	:= $(libdir)/lib$(NAME)$(LDEXT)
# ----------------------------------------------------------------------------
all: $(LIBRARY)

linkdef: $(LINKDEF)

$(LIBRARY)	: $(OBJECTS)
	@echo ""
	@echo "=> Linking shared library $@"
	$(LD) $(LDFLAGS) $^ $(LIBS)  -o $@

$(OBJECTS)	: %.o	: 	%.cc
	@echo ""
	@echo "=> Compiling $<"
	$(CXX) $(CXXFLAGS) $(CPPFLAGS) -c $< -o $@

$(DICTIONARIES)	: $(srcdir)/%_dict.cc	: $(srcdir)/%.cpp $(LINKDEF)
	@echo ""
	@echo "=> Building dictionary $@"
	$(ROOTCINT) -f $@ -c $(CPPFLAGS) $+
	find $(srcdir) -name "*.pcm" -exec mv {} $(libdir) \;

$(LINKDEF): $(CPPSRCS)
	@echo ""
	@echo "=> Building $@"
	@echo "from string import split"          > .tmp.py
	@echo "filenames = split('$+')"          >> .tmp.py
	@echo "def nameonly(name):"              >> .tmp.py
	@echo "    from posixpath import splitext, split" >> .tmp.py
	@echo "    return splitext(split(name)[1])[0]"    >> .tmp.py
	@echo "names = map(nameonly, filenames)" >> .tmp.py
	@echo "print names"                      >> .tmp.py	
	@echo "linkdef = '''#ifdef __CINT__"     >> .tmp.py
	@echo "#pragma link off all globals;"    >> .tmp.py
	@echo "#pragma link off all classes;"    >> .tmp.py
	@echo "#pragma link off all functions;"  >> .tmp.py
	@echo "'''"                              >> .tmp.py
	@echo "for x in names:"                  >> .tmp.py
	@echo "  linkdef += '#pragma link C++ function %s;\\@' % x" >> .tmp.py
	@echo "linkdef  += '#endif\\@'"          >> .tmp.py
	@echo "open('$@', 'w').write(linkdef)"   >> .tmp.py
	@sed -e "s/@/n/g" .tmp.py > linkdef.py
	@python linkdef.py

clean:
	rm -rf $(libdir)/* $(srcdir)/*_dict*.* $(srcdir)/*.o $(srcdir)/linkdef.h
