#include <stdlib.h>
#include "TStopwatch.h"

double metd(double f_pf_met,
	    int first=0, int last=99);

double m4lmela(double f_mass4l,
	       double f_D_bkg_kin,
	       int first=0, int last=99);

double m4lmelamet(double f_mass4l,
                  double f_D_bkg_kin,
                  double f_pfmet,
                  int first=0, int last=99);
void testcall()
{
  TStopwatch swatch;
  int n=500000;
  for(int ii=0; ii < n; ii++)
    {
      if ( ii % 100000 == 0 ) printf("%10d\n", ii);
      
      double x = 100 + ii % 200;
      double y = (double)(ii % 1000) / 1000;
      double z = x;
      metd(x);
      m4lmela(x, y);
      m4lmelamet(x, y, z);
    }
  double t = swatch.RealTime() / n;
  t *= 1.e6;
  printf("execution time: %10.2f microsecond / event\n", t);
  exit(0);
}
