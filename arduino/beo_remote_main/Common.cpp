#include "Common.h"

String pad(String str) {
  if (str.length() == 1) {
    return "0" + str;
  }
  
  return str;
}
