#pragma once
#include<stdarg.h>

#define NAME_LEN_ERR -1

void err_quit(const char* fmt, ...) {
    va_list ap;

    va_start(ap, fmt);
    fprintf(stderr, fmt, ap);
    va_end(ap);
    exit(1);
}

void err_sys(const char* fmt, ...) {
    va_list ap;

    va_start(ap, fmt);
    fprintf(stderr, fmt, ap);
    va_end(ap);
    exit(1);
}

