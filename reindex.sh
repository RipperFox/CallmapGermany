#!/bin/bash
echo "Regenerating indices"
sqlite3 calls.db "
DROP INDEX IF EXISTS Street_Zip;
DROP INDEX IF EXISTS Calls_Location;
DROP INDEX IF EXISTS Locations_Id;
CREATE INDEX Street_Zip on Locations(Street, Zip);
CREATE INDEX Calls_Location on Calls(Location);
CREATE INDEX Locations_id on Locations(id);
REINDEX;"
echo "Done"
echo "Current schema:"
sqlite3 calls.db '.schema'


