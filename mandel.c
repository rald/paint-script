/**
* Mandelbrot set implementation in TURBO-C
*  
* To compile follow these steps:
*	> tcc -ml mandel.c
*	> tlink c0m mandel, mandel,, emu fp87 mathm graphics cm
*	> mandel
*
* By Robert Lafore - 1989
*	for the book Turbo C - Programming for the PC
*/

#include <graphics.h>

#define XMAX 100 /* change these to change size */
#define YMAX 100	/*	of picture */
#define MAXCOUNT 16 /* number of iterations */

void main() {
	
	int x, y;				/* location of pixel on screen */
	float xscale, yscale;	/* distance between pixels */
	float left, top;		/* location of top left corner */
	float xside, yside;		/* length of sides */
	float zx, zy;			/* real and imag parts of z */
	float cx, cy;			/* real and imag parts of c */
	float tempx;			/* briefly holds zx */
	int count;				/* number of iterations */
	int driver, mode;		/* graphics driver and mode */

	left = -2.0;			/* coordinates for entire */
	top = 1.25;				/*	mandelbrot set */
	xside = 2.5;			/*	change to see details */
	yside = -2.5;			/* 	of set */
	xscale = xside / XMAX;  
	yscale = yside / YMAX;

	driver = EGA;			/* set driver and mode */
	mode = EGAHI;
	initgraph( &driver, &mode, "C:\\TURBOC\\BGI" );

	rectangle( 0, 0, XMAX+1, YMAX+1 );

	for( y = 1; y <= YMAX; y++ ) {			/* for each pixel column */
		for( x = 1; x <= XMAX; x++ ) {		/* for each pixel row */
			cx = x*xscale + left;			/* set c to pixel location */
			cy = y*yscale + top;
			zx = zy = 0;					/* set z = 0 */
			count = 0;						/* reset count */
											/* size of z < 2 */
			while( zx*zx + zy*zy < 4 && count < MAXCOUNT ) {
				tempx = zx*zx - zy*zy + cx;	/* set z = z^2 + c */
				zy = 2*zx*zy + cy;
				zx = tempx;
				count++;					/* another iteration */
			}
			putpixel( x, y, count ); 		/* color is count */

			if( kbhit() ) {					/* to abort program */
				closegraph();				/*	before picture is finished */
				exit( 0 );					
			}
		}
	}

	getche();			/* keep picture untile keypress */
	closegraph();		/* close graphics system */
}
