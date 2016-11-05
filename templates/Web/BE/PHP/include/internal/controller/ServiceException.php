<?php
require_once( INTERNAL_ROOT_DIR . '/utils/RethrownException.php');

/**
 * This Exceptions is thrown by a Service. That means that we are going to return 
 * just the message, not render a message
 */
class ServiceException extends RethrownException {
}