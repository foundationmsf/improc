# Adding new training data

1. Create a subfolder of this folder named `ast_pictures` and put the AST pictures there.
2. Run `step_1_crop_pellets_from_ast_pictures.py`
   * You might need to install improc Python bindings first, see [here](../../README.md).
   * See the script header for what it does. 
3. Manually check all subfolders in `pellets`, move the pellets to the right subfolder if wrong.
   * Make sure there are no wrong labels, it has a big impact on the training.
4. Run `step_2_split_into_train_and_valid.py`. 
   * See the script header for what it does. 
   * The script lists the number of samples in each data dir, which can help you decide about the weights for training. 
5. Now you can re-train the model, see [here](../README.md). 
