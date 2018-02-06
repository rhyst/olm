@ECHO OFF
cmd /k ".env\Scripts\activate & python olm/olm.py ../testsite & deactivate"
exit 0