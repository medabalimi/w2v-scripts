L=$1
python3.7 utils/kaldi2wav2vec_manifest_simple.py --audio_output_folder audio --manifest_folder manifest/blind_test /opt/is21/subtask2/blind_test/$L/files /opt/is21/subtask2/blind_test/$L/


for ext in tsv ltr wrd ; 
  do 
	  ln -sf ../blind_test/manifest/train.$ext blind_test.$ext;
  done

./infer_lm.sh model/v1.pt

python3 ./utils/wav2vec2kaldi.py manifest/train/blind_test.tsv  eval/$L/hypo.word-v1.pt-blind_test.txt  eval/$L/$L.txt
