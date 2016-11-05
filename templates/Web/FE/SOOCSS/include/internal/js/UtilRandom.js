/**
 * Utilities for random numbers
 */
UtilRandom = {};


/* Get a random integer in the interval [min, max] */
UtilRandom.getInteger = function(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}