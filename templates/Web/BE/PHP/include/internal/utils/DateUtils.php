<?php
class DateUtils {
  public static function ddmmyyyyHHMM2Timestamp($ddmmyyyy, $hhmm, $tz="+00:00") {
    $fecha = DateTime::createFromFormat('d/m/Y H:i P', $ddmmyyyy . ' ' . $hhmm . ' ' . $tz);
    return $fecha->format('U');
  }
}
?>
