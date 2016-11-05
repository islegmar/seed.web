<?php
/**
 * Exception thrown when an action needs to have an authenticated user and 
 * the current one is an anonymous one. 
 * In such case, the action could be ask the user to authenticate himself.
 */
class UserNotAuthenticatedException extends Exception {
}
?>