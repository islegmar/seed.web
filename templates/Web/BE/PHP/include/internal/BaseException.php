<?php
/**
 * This exception allow to add new error messages
 */
class BaseException extends Exception
{
	public function addMessage($msg) {
		$this->message .= $msg;	
	}
}
?>
