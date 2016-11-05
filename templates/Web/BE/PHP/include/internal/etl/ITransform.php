<?php

/**
 * Convert a single value into an object
 */
interface ITransform  {
	// Receives a configuration and configure the transformer to be able to do
	// the transform operation
	// The configuration is a JSON (an Object) NOT array
	public function config($config);

	// Transform a value into something else (fex. a String that represents a date
	// into a Date using a format provided in the config....)
	public function transform($value);
}
?>