#!/bin/bash
#
###############################################################
# Program that calculates the BioBit value of a certain genome 
#
# AUTHOR: Pablo Román-Escrivá
# DATE: 06 July 2022
# UPDATE: 03 October 2023 
#   - Changed upper limit calculation (several genomes)
#   - Added Genome ID to output when upper limit is reached
# UPDATE: 9 November 2023
#   - Error management when zipped file is corrupt
#   - Improved handling of errors
#
# REQUIREMENTS: K-Mer Counter (KMC) ver. 3.2.1 or higher (https://github.com/refresh-bio/KMC)
# 
###############################################################
export LC_NUMERIC="en_US.UTF-8"
n_threads=1
mem_gb=2
output_all=0
usage()
{
  echo "Usage: ./subscript_biobit_kmc.sh [ -t | --threads NUM_THREADS ]
                    [ -m | --mem_gb GB_MEMORY (minimum 2 GB) ]
                    [ -o | --output_all (outputs also intermediate results and percentage of hapaxes)]
                    [ -f | --file FASTA_FILE (fa, fasta, fna, and gz versions) ]"
  exit 2
}
PARSED_ARGUMENTS=$(getopt -a -n $0 -o t:m:of: --long threads:,mem_gb:,output_all,file: -- "$@")
eval set -- "$PARSED_ARGUMENTS"
while :
do
  case "$1" in
    -t | --threads)     n_threads="$2"  ; shift 2 ;;
    -m | --mem_gb)      mem_gb="$2"     ; shift 2 ;;
    -f | --file)        archivo="$2"    ; shift 2 ;;
    -o | --output_all)  output_all=1    ; shift   ;;
    --) shift; break ;;
    # If invalid options were passed, then getopt should have reported an error,
    # which we checked as VALID_ARGUMENTS when getopt was called...
    *) echo "Unexpected option: $1 - this should not happen."
       usage ;;
  esac
done
if [ -z "$archivo" ] || [ "$mem_gb" -lt 2 ]; then
    usage
fi

mkdir -p results
chmod +x results

if test -f "$archivo"; then
    if [[ ! $archivo =~ .*\.(fa|fna|fasta|fa.gz|fna.gz|fasta.gz) ]]; then 
        >&2 echo "ERROR - $archivo is not not a FASTA file (fa, fna, fasta, fa.gz, fna.gz, fasta.gz)" 
        exit 1
    fi
else 
    >&2 echo "ERROR - $archivo doesn't exist or cannot be accessed"
    exit 1
fi
file_ext=$(basename -- "$archivo")
file_ext=${file_ext%%.*}
filename=$(echo $file_ext | awk -F _ '{print $1 (NF>1? FS $2 : "")}')
# The script approximates the size of the genome as the number of ACGT bases 
n_bases=$(zgrep -v -s ">" $archivo | tr -cd "A|C|G|T|g|c|t|a" | wc -c)
# If zipped file is corrupt, exit with an error (zgrep check)
if [[ -z "$n_bases" ]]
then
    >&2 echo "ERROR - problem with zipped file $archivo"
    exit 1
fi
if [[ ! -f results_bb.csv ]]
then
    echo "accession,k1,ek1,ek2,e2lg,af,lx,eh,lg,ec,ac,ralg,raaf,termino,bb,perc_hap" >> results_bb.csv
fi
#echo "n_bases $n_bases"
two_lg=$(awk -v a="$n_bases" 'BEGIN{printf "%.9f", log(a)/log(2)}')
#echo "two_lg $two_lg"
two_lg_round=$(printf '(%s+0.5)/1\n' $two_lg | bc) 
#echo "two_lg_round $two_lg_round"
k1=$(awk -v two_lg=$two_lg 'BEGIN{print $1, $2, int(two_lg)}' | sed 's/^ *//g')
#echo "k1 $k1"
k2=$(($k1+1))
#echo "k2 $k2"
#unique is the number of different kmers found in the genome
#total is the total number of kmers found in the genome
upper_limit=$(awk -v n_bases="$n_bases" 'BEGIN{printf "%d", (n_bases/10)}')
read -d "\n" unique total <<< $(kmc -k$k1 -fm -b -ci1 -cs$upper_limit -hp -t$n_threads -m$mem_gb $archivo output results | tail -4 | head -2 | awk -F " " '{print $NF}')
# If zipped file is corrupt, exit with an error (gzip check)
if [[ -z "$unique" ]]
then
    >&2 echo "ERROR - problem with zipped file $archivo"
    exit 1
fi
#echo "unique $unique"
#echo "total $total"
lx=$(awk -v n_bases="$n_bases" -v unique="$unique" 'BEGIN{printf "%.9f", (n_bases/unique)}')
#echo "lx $lx"
lg=$(awk -v two_lg="$two_lg" 'BEGIN{printf "%.9f", (two_lg / 2)}')
#echo "lg $lg"
ralg=$(awk -v lg="$lg" 'BEGIN{printf "%.9f", sqrt(lg)}')
#echo "ralg $ralg"
kmc_tools -hp transform output histogram results.txt -cx$upper_limit> /dev/null
# Uncomment the next line if the actual frequency table (without zeros) is needed
#kmc_dump output "$filename"_k1.txt
if [[ $(tail -1 results.txt | awk '{print $2}') -ne 0 ]]
then
    >&2 echo "ERROR - increase upper limits for $filename"
    exit 1
fi
if [[ $two_lg_round -eq $k1 ]] 
then
    num_hap=$(head -1 results.txt | awk '{print $2}')
    perc_hap=$(awk -v num_hap="$num_hap" -v total="$total" 'BEGIN{printf "%.9f", (num_hap / total) * 100}')
fi
#echo "perc_hap $perc_hap"
ek1=$(awk '$2>0' results.txt | awk -v total="$total" 'BEGIN{FS="\t"; sum=0} {sum-=$2*$1*((log($1)/log(2))-(log(total)/log(2)))} END{printf "%.9f", sum/total}')
#echo "ek1 $ek1"
read -d "\n" unique total <<< $(kmc -k$k2 -fm -b -ci1 -cs$upper_limit -hp -t$n_threads -m$mem_gb $archivo output results | tail -4 | head -2 |  awk -F " " '{print $NF}')
#echo "unique $unique"
#echo "total $total"
kmc_tools -hp transform output histogram results.txt -cx$upper_limit> /dev/null
# Uncomment the next line if you need the actual frequency table (without zeros)
#kmc_dump output "$filename"_k2.txt
if [[ $(tail -1 results.txt | awk '{print $2}') -ne 0 ]]
then
    >&2 echo "ERROR - increase upper limits for $filename"
    exit 1
fi
if [[ $two_lg_round -eq $k2 ]] 
then
    num_hap=$(head -1 results.txt | awk '{print $2}')
    perc_hap=$(awk -v num_hap="$num_hap" -v total="$total" 'BEGIN{printf "%.9f", (num_hap / total) * 100}')
fi
ek2=$(awk '$2>0' results.txt | awk -v total="$total" 'BEGIN{FS="\t"; sum=0} {sum-=$2*$1*((log($1)/log(2))-(log(total)/log(2)))} END{printf "%.9f", sum/total}')
#echo "ek2 $ek2"
e2lg=$(awk -v ek1="$ek1" -v ek2="$ek2" -v two_lg="$two_lg" -v k1="$k1" 'BEGIN{printf "%.9f",  ek1 + (ek2 - ek1) * (two_lg - k1)}')
#echo "eekk $eekk"
ec=$(awk -v e2lg="$e2lg" -v lg="$lg" 'BEGIN{printf "%.9f", e2lg - lg}')
#echo "ec $ec"
af=$(awk -v two_lg="$two_lg" -v e2lg="$e2lg" -v lg="$lg" 'BEGIN{printf "%.9f", (two_lg - e2lg) / lg}')
#echo "af $af"
ac=$(awk -v lg="$lg" -v af="$af" 'BEGIN{printf "%.9f", af*lg}')
#echo "ac $ac"
eh=$(awk -v ec="$ec" -v ac="$ac" -v lg="$lg" 'BEGIN{printf "%.9f", (ec - ac) / lg}')
#echo "eh $eh"
raaf=$(awk -v af="$af" 'BEGIN{printf "%.9f", sqrt(af)}')
#echo "raaf $raaf"
termino=$(awk -v af="$af" 'BEGIN{printf "%.9f", (1-(2*af))^3}')
#echo "termino $termino"
bb=$(awk -v ralg="$ralg" -v raaf="$raaf" -v termino="$termino" 'BEGIN{printf "%.9f", ralg*raaf*termino}')
if [ $output_all == 1 ]; then 
    echo "$filename,$k1,$ek1,$ek2,$e2lg,$af,$lx,$eh,$lg,$ec,$ac,$ralg,$raaf,$termino,$bb,$perc_hap" >> results_bb.csv
else 
    echo "$filename,$bb" >> results_bb.csv
fi
rm output.kmc_pre
rm output.kmc_suf
rm results.txt
rmdir results
