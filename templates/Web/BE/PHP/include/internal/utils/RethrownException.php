<?php
/**
 * This Exceptions is rethrown of any other, that is the one that really matters.
 * This is used as base class
 */
class RethrownException extends Exception {
	protected $originalException = null;
	public function __construct($originalException ) {
		$this->originalException = $originalException;
	}
	
	public function __toString() {
		return $this->originalException.__toString();
	}
}