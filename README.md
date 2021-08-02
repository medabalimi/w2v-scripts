# w2v-scripts
Scripts for processing data for use with wav2vec

This repo consists of scripts required to convert data from kaldi format to wav2vec manifest files and to convert the evaluation results to kaldi compatible ones.

# Converting kaldi based data format to wav2vec
The script kaldi2wav2vec_manifest_simple.py helps generate manifest files from kaldi files. Run it with --help to check the options.



# Generating character/graphemic lexicon
You would need a lexicon (either mapping to character/grapheme) when used with a language model. get_lexicon.py generates one for you. You can either provide a text corpus or a list of words and it will generate the lexicon automatically.

# Data augmentation
Given no of augmentations, it generates augmented data (along with the augmented manifest). Currently augmentations include time dropout, pitch and speed perturbations.

# Generating kaldi format hypothesis output
When evaluation submissions are required in kaldi format, wav2vec2kaldi.py can be used to generate them. Given the tsv file and the word hypothesis file, it generates the output 


# Example
Please have a look at generate_evalout.sh for how to create manifests or kaldi hypothesis outputs
