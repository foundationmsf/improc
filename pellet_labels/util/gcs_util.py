from tensorflow.python.lib.io import file_io
import os
import subprocess


def download_file_from_gcs(source, destination):
  if not os.path.exists(destination):
    subprocess.check_call([
        'gsutil',
        'cp',
        source, destination])
  else:
    print('File %s already present locally, not downloading' % destination)


# h5py workaround: copy local models over to GCS if the job_dir is GCS.
def copy_file_to_gcs(local_path, gcs_path):
  with file_io.FileIO(local_path, mode='rb') as input_f:
    with file_io.FileIO(gcs_path, mode='w+') as output_f:
      output_f.write(input_f.read())


def append_id(filename, index):
  """
  Returns the `filename` with `index` appended just before the file extension.
  E.g. "image.png", 3 -> "image_3.png".
  """
  name, ext = os.path.splitext(filename)
  return "{name}_{id}{ext}".format(name=name, id=index, ext=ext)


def load_models_from_gcs(
    job_dir, model_folder, model_name, working_dir, n_ensemble):
  job_name = job_dir[job_dir.rfind('/') + 1:]
  model_paths = []
  for i in range(1, n_ensemble + 1):
    gcs_path = os.path.join(job_dir, model_folder + str(i), model_name)
    local_path = os.path.join(working_dir, "ensemble_models", job_name,
                              append_id(model_name, i))
    download_file_from_gcs(gcs_path, local_path)
    model_paths.append(local_path)
  return model_paths
