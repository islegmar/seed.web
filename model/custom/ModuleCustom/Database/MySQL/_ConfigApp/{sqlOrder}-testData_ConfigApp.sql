UPDATE _ConfigApp 
   SET Path4I18N='{Environ(PRJ_HOME)}/data/i18n',
       ServerReturnAlwaysI18N=1,
       BaseURL = 'http://localhost/webrad';
