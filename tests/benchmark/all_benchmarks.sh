OUTPUT=all_benchmarks.txt

{
  echo ""
  date
  set -x
  ./benchmark.sh -c annotations/koutiala/Koutiala_BloodAgar_Golden.yml -i ~/Downloads/Koutiala\ -\ Bio-Rad
  ./benchmark.sh --nobuild -c annotations/creteil_nature_com/Creteil_Nature_Com.yml -i annotations/creteil_nature_com/images/blood_agar/
  ./benchmark.sh --nobuild -c annotations/amman/Amman_BloodAgar_Golden.yml -i annotations/amman/images/blood_agar/benchmark
  ./benchmark.sh --nobuild -c annotations/amman/Amman_BloodAgar_Discovery.yml -i annotations/amman/images/blood_agar/discovery
} >> $OUTPUT
