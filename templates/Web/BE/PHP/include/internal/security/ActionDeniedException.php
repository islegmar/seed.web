<?php
/**
 * This exception is the one that the checkSecurity methods should throw when 
 * an action can not be performed.
 * This should could be called "UserNotAuthorizedException" in in such 
 * cases it has no sense to ask the user to authenticate himself (in the 99% of
 * the cases he will be an authenticated user).
 */
class ActionDeniedException extends Exception {
}
?>