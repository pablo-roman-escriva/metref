#!/bin/bash
#
###############################################################
# Program that calculates the GS value of a certain genome 
#
# AUTHOR: Pablo Román-Escrivá
# DATE: 05 December 2023
#
# REQUIREMENTS: K-Mer Counter (KMC) ver. 3.2.1 or higher (https://github.com/refresh-bio/KMC)
# 
###############################################################
export LC_NUMERIC="en_US.UTF-8"
n_threads=2
mem_gb=2
output_tables=0
k=0
provided_k=true
declare -a KS=()
PARSED_ARGUMENTS=$(getopt -a -n $0 -o t:m:f:ok: -- "$@")
eval set -- "$PARSED_ARGUMENTS"
while :
do
  case "$1" in
    -t)   n_threads="$2"     ; shift 2 ;;
    -m)   mem_gb="$2"        ; shift 2 ;;
    -f)   archivo="$2"       ; shift 2 ;;
    -o)   output_tables=1    ; shift   ;;
    -k)   k="$2"             ; shift 2 ;;
    --) shift; break ;;
    # If invalid options were passed, then getopt should have reported an error,
    # which we checked as VALID_ARGUMENTS when getopt was called...
    *) echo "Unexpected option: $1 - this should not happen."
       usage ;;
  esac
done
if [ -z "$archivo" ] || [[ $n_threads -lt 2 ]] || [[ $mem_gb -lt 2 ]] || [[ $k -ge 19 ]]; then
    exit 1
fi

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
#echo "n_bases $n_bases"
upper_limit=$(awk -v n_bases="$n_bases" 'BEGIN{printf "%d", (n_bases / 10)}')
#echo "upper_limit $upper_limit"

if [[ $k -eq 0 ]]
then
    provided_k=false
    k=($(echo | awk -v a="$n_bases" 'BEGIN{printf "%d", int(((log(a)/log(4))-3)+0.5)}'))
    #echo "k $k"
fi

if [[ ! -f results_gs.csv ]]
then
    echo "accession,G,k,EV,found,entropy,GS,GS_rnd,NGS" >> results_gs.csv
fi

found_max=false
direction_left=false
direction_right=false
first_iteration=true
second_iteration=false
prev_ngs=0
prev_gs=0
prev_gsrnd=0
prev_ev=0
prev_found=0
prev_entropy=0

while true
do
    mkdir -p results_$filename
    chmod +x results_$filename
    #unique is the number of different kmers found in the genome
    #total is the total number of kmers found in the genome
    read -d "\n" unique total <<< $(kmc -k$k -b -fm -ci1 -cs$upper_limit -hp -t$n_threads -m$mem_gb $archivo output_$filename results_$filename | tail -4 | head -2 | awk -F " " '{print $NF}')
    >&2 echo -n "Trying k=$k for $filename "
    # If zipped file is corrupt, exit with an error (gzip check)
    if [[ -z "$unique" ]]
    then
        >&2 echo "ERROR - problem with zipped file $archivo"
        exit 1
    fi
    #echo "unique $unique"
    #echo "total $total"
    found=$(awk -v unique="$unique" -v k="$k" 'BEGIN{printf "%.9f", (unique / (4^k))*100}')
    #echo "found $found"
    kmc_tools -hp transform output_$filename histogram results_$filename.txt -cx$upper_limit> /dev/null
    if [ $output_tables == 1 ]; then 
        mkdir -p tables
        salida=tables/"$filename"_k"$k".txt
        kmc_dump output_$filename $salida
    fi

    if [[ $(tail -1 results_$filename.txt | awk '{print $2}') -ne 0 ]]
    then
        >&2 echo "ERROR - increase upper limits for $filename"
        exit 1
    fi
    ev=$(awk -v total="$total" -v k="$k" 'BEGIN{printf "%.9f", (total / (4^k))}')
    #echo "ev $ev"
    missing=$(awk -v unique="$unique" -v k="$k" 'BEGIN{printf "%.9f", ((4^k) - unique)}')
    #echo "missing $missing"
    sum_no_missing=$(awk '$2>0' results_$filename.txt | awk -v ev="$ev" 'BEGIN{FS="\t"; sum=0} function abs(v) {return v < 0 ? -v : v} {sum+=$2*abs(($1/ev)-1)} END{printf "%.9f", sum}')
    #echo "sum_no_missing $sum_no_missing"
    sum=$(awk -v sum_no_missing="$sum_no_missing" -v missing="$missing" 'BEGIN{printf "%.9f", (sum_no_missing + missing)}')
    #echo "sum $sum"
    gs=$(awk -v sum="$sum" -v k="$k" 'BEGIN{printf "%.9f", (sum / (4^k))}')
    #echo "gs $gs"
    entropy=$(awk '$2>0' results_$filename.txt | awk -v total="$total" 'BEGIN{FS="\t"; sum=0} {sum-=($2/total)*(log($2/total)/log(4))} END{printf "%.9f", sum}')
    #echo "sum_no_missing $sum_no_missing"

    rm output_$filename.kmc_pre
    rm output_$filename.kmc_suf
    rm results_$filename.txt
    rm -rf results_$filename

    mkdir -p results_$filename
    chmod +x results_$filename

    ./RandomADN3 $total

    read -d "\n" unique_rnd total_rnd <<< $(kmc -k$k -b -fm -ci1 -cs$upper_limit -hp -t$n_threads -m$mem_gb ADNR_NN_$total.fa output_$filename results_$filename | tail -4 | head -2 | awk -F " " '{print $NF}')
    #echo $unique_rnd
    #echo $total_rnd
    kmc_tools -hp transform output_$filename histogram results_$filename.txt -cx$upper_limit> /dev/null
    ev=$(awk -v total_rnd="$total_rnd" -v k="$k" 'BEGIN{printf "%.9f", (total_rnd / (4^k))}')
    #echo "ev $ev"
    missing_rnd=$(awk -v unique_rnd="$unique_rnd" -v k="$k" 'BEGIN{printf "%.9f", ((4^k) - unique_rnd)}')
    #echo "missing $missing"
    sum_no_missing_rnd=$(awk '$2>0' results_$filename.txt | awk -v ev="$ev" 'BEGIN{FS="\t"; sum=0} function abs(v) {return v < 0 ? -v : v} {sum+=$2*abs(($1/ev)-1)} END{printf "%.9f", sum}')
    #echo "sum_no_missing $sum_no_missing"
    sum_rnd=$(awk -v sum_no_missing_rnd="$sum_no_missing_rnd" -v missing_rnd="$missing_rnd" 'BEGIN{printf "%.9f", (sum_no_missing_rnd + missing_rnd)}')
    #echo "sum $sum"
    gs_rnd=$(awk -v sum_rnd="$sum_rnd" -v k="$k" 'BEGIN{printf "%.9f", (sum_rnd / (4^k))}')
    #echo "gs $gs"
    rm ADNR_NN_$total.fa
    rm output_$filename.kmc_pre
    rm output_$filename.kmc_suf
    rm results_$filename.txt
    rm -rf results_$filename

    ngs=$(awk -v gs="$gs" -v gs_rnd="$gs_rnd" 'BEGIN{printf "%.9f", (gs - gs_rnd)}')
    >&2 echo "$ngs"
    if [ "$provided_k" = false ]
    then
        if [ "$first_iteration" = true ]
        then
            prev_ngs=$ngs
            prev_gs=$gs
            prev_gsrnd=$gs_rnd
            prev_ev=$ev
            prev_entropy=$entropy
            prev_found=$found
            k=$(($k-1))
            first_iteration=false
            second_iteration=true
        else
            if [ "$second_iteration" = true ]
            then
                if [ 1 -eq "$(echo "$ngs > $prev_ngs" | bc)" ]
                then
                    direction_left=true
                    prev_ngs=$ngs
                    prev_gs=$gs
                    prev_gsrnd=$gs_rnd
                    prev_ev=$ev
                    prev_entropy=$entropy
                    prev_found=$found
                    k=$(($k-1))
                    second_iteration=false
                    continue
                else
                    direction_right=true
                    k=$(($k+2))
                    second_iteration=false
                    continue
                fi
            else
                if [ "$direction_left" = true ]
                then
                    if [ 1 -eq "$(echo "$ngs < $prev_ngs" | bc)" ]
                    then
                        ngs=$prev_ngs
                        gs=$prev_gs
                        gs_rnd=$prev_gsrnd
                        ev=$prev_ev
                        entropy=$prev_entropy
                        found=$prev_found
                        k=$(($k+1))
                        >&2 echo "Best k for $filename $k"
                        break
                    else
                        prev_ngs=$ngs
                        prev_gs=$gs
                        prev_gsrnd=$gs_rnd
                        prev_ev=$ev
                        prev_entropy=$entropy
                        prev_found=$found
                        k=$(($k-1))
                    fi
                fi
                if [ "$direction_right" = true ]
                then
                    if [ 1 -eq "$(echo "$ngs < $prev_ngs" | bc)" ]
                    then
                        ngs=$prev_ngs
                        gs=$prev_gs
                        gs_rnd=$prev_gsrnd
                        ev=$prev_ev
                        entropy=$prev_entropy
                        found=$prev_found
                        k=$(($k-1))
                        >&2 echo "Best k for $filename $k"
                        break
                    else
                        prev_ngs=$ngs
                        prev_gs=$gs
                        prev_gsrnd=$gs_rnd
                        prev_ev=$ev
                        prev_entropy=$entropy
                        prev_found=$found
                        k=$(($k+1))
                    fi
                fi
            fi
        fi
    else 
        break
    fi
done
echo "$filename,$n_bases,$k,$ev,$found,$entropy,$gs,$gs_rnd,$ngs" >> results_gs.csv
