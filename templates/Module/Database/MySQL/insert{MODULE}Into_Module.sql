-- Insert this module config into the table _Module
DELETE FROM _Module WHERE Name='{MODULE}';
INSERT INTO _Module (Name, Config) VALUES ('{MODULE}', '{ModuleConfig}');