from sorting.settings import MOUNTAINSORT_SETTINGS

from subprocess import check_output
import os.path
import json
from collections import namedtuple

class ProjectMisconfigured(Exception):
    pass

class DoesNotExist(Exception):
    pass

class PipelineDoesNotExist(DoesNotExist):
    pass

class DatasetDoesNotExist(DoesNotExist):
    pass

class ProjectDoesNotExist(DoesNotExist):
    pass

class Kron:
  mountainprocess_path = os.path.join(MOUNTAINSORT_SETTINGS["BASE_DIR"], "bin", "mountainprocess")
  kron_run_path = os.path.join(MOUNTAINSORT_SETTINGS["BASE_DIR"], "bin", "kron-run")
  pipelines_file = "pipelines.txt"
  datasets_file = "datasets.txt"

  def __init__(self, projectPath, **kwargs):
    self.projectPath = projectPath
    self.kwargs = kwargs
    if not os.path.isdir(self.absolutePath): raise ProjectDoesNotExist()
    if not os.path.isfile(os.path.join(self.absolutePath, self.pipelines_file)): raise ProjectMisconfigured()
    self.refresh()

  def refresh(self):
    self.datasetList = self.get_datasets()
    self.pipelineList = self.get_pipelines()


  @property
  def pipelines(self):
    return self.pipelineList

  @property
  def datasets(self):
    return self.datasetList

  @property
  def absolutePath(self):
    return os.path.join(MOUNTAINSORT_SETTINGS["BASE_DIR"], self.projectPath)

  def get_pipelines(self):
    ret = []
    try:
     with open(os.path.join(self.absolutePath, self.pipelines_file)) as f:
      for line in f:
        tokens = line.rstrip().split(" ",1)
        ret.append(tokens[0])
    except:
      return []
    return ret

  def get_datasets(self):
    ret = []
    try:
     with open(os.path.join(self.absolutePath, self.datasets_file)) as f:
      for line in f:
        tokens = line.rstrip().split(" ",1)
        ret.append(tokens[0])
    except:
      return []
    return ret

  def get_kron_run_path(self):
    if not os.path.isfile(self.kron_run_path): raise DoesNotExist()
    return self.kron_run_path

  def get_mountainprocess_path(self):
    if not os.path.isfile(self.mountainprocess_path): raise DoesNotExist()
    return self.mountainprocess_path


  def start(self, pipeline, dataset):
    if pipeline not in self.pipelines: raise PipelineDoesNotExist()
    if dataset not in self.datasets: raise DatasetDoesNotExist()
    kron_path = self.get_kron_run_path()
    cwd = os.getcwd()
    os.chdir(self.absolutePath)
    try:
      output = check_output( [ kron_path, pipeline, dataset, '--_return' ])
      return json.loads(output.decode('utf-8'), object_hook=lambda d: namedtuple('KRONResult', d.keys())(*d.values()))
    except:
      return None
    finally:
      os.chdir(cwd)

  def script_status(self, script_id):
    mp = self.get_mountainprocess_path()
#    if isinstance(script_id, 'KRONResult'):
#      script_id = script_id.script_id
#    try:
    output = check_output( [ mp, 'daemon-state', '--script_id={}'.format(script_id) ])
    return json.loads(output.decode('utf-8'), object_hook=lambda d: namedtuple('ScriptStatus', d.keys())(*d.values()))
#    return None
#    except:
#      return None
