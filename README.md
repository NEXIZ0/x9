wellcom to x9 nexiz version

##add it in zshrc
```
alias mass_x9="/nexiz/Tools/x9/mass_x9.py"
```
##command usage

###automate
```
mass_x9 <domain> [or] mass_x9 <domain> -katana

cat x9.res

python3 clean.py
```
###manuaaly
```
python3 x9_p1.php <domain> [or] python3 x9_p1.php <domain> -katana

python3 x9_p2.py -L <domain>.passiv -r parameters.txt -c 40

cat run.x9 | nuclei -t nuclei_xss.yaml -silent | tee x9.res

python3 clean.py
```
