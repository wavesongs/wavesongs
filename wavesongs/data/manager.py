"""
Query and download data from Xeno Canto
"""
import shutil

import pandas as pd

from os.path import basename
from pathlib import Path, PosixPath

from maad.util import xc_download, xc_multi_query

#%%
def download_audios(
    df_dataset: pd.DataFrame,
    rootdir: str = "./assets/audio", 
    dataset_name: str = "",
    overwrite: bool = True,
    save_csv: bool = True,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Download audios from `Xeno Canto <https://xeno-canto.org/>`_  with 
    `maad.utils.xc_download <https://scikit-maad.github.io/util.html#xeno-canto>`_.

    Args:
        df_dataset (pd.DataFrame):
            Data Frame with the information to download.
        country (str, optional):
            _description_. Defaults to "Colombia".
        rootdir (str, optional):
            _description_. Defaults to "./assets/audio".
        dataset_name (str, optional):
            _description_. Defaults to ''.
        overwrite (bool, optional):
            _description_. Defaults to False.
        save_csv (bool, optional):
            _description_. Defaults to True.
        verbose (bool, optional):
            _description_. Defaults to True.

    Returns:
        df_audios (pd.DataFrame) : Data Frame
    """
    df_audios = xc_download(
      df=df_dataset, 
      rootdir=rootdir,
      dataset_name=dataset_name,
      overwrite=overwrite,
      save_csv=save_csv,
      verbose=verbose,
    )

    gen, sp, en = df_dataset.iloc[0][["gen", "sp", "en"]].values

    downloaded_folder = f"{gen} {sp}_{en}"
    
    # can be improved
    dataset_path = f"{rootdir}/{downloaded_folder}" if dataset_name=="" \
                    else f"{rootdir}/{dataset_name}/{downloaded_folder}"
    all_filles = Path(dataset_path).glob("**/*")
    if dataset_name=="": 
        dataset_name = f"{gen}_{sp}".lower()
    Path(f"{rootdir}/{dataset_name}").mkdir(parents=True, exist_ok=True)
    for file in all_filles:
        file_name = str(file).split("/")[-1]
        new_name = f"{rootdir}/{dataset_name}/{file_name}" if dataset_name!="" \
                    else f"{rootdir}/{file_name}"
        Path(file).rename(new_name)
        print(f"Audio saved at {new_name}.")
    shutil.rmtree(dataset_path)

    return df_audios

# %%
def query_audios(
    specie_names: list[str] | list[list[str]],
    max_nb_files: int | None = None,
    random_seed: int = 2025,
    info: dict = {},
    format_time=True,
    format_date=True,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Query me from `Xeno Canto <https://xeno-canto.org/>`_ 
    with `maad.utils.xc_multi_query <https://scikit-maad.github.io/util.html#xeno-canto>`_.
    
    Args:
        specie_names (list[str], list[list[str]]): 
            List with english and scientific specie names.
        max_nb_files (int, optional):
            Maximum number of files to download. Defaults to None.
        random_seed (int, optional):
            Random seed. Defaults to 2025.
        info (dict, optional):
            Dictionary with information to query. Defaults to {}.
        format_time (bool, optional):
            Format time. Defaults to True.
        format_date (bool, optional):
            Format date. Defaults to True.
        verbose (bool, optional):
            Verbose. Defaults to True.

    Returns:
        df_query (pd.DataFrame) : Data Frame
    """
    if type(specie_names[0])==str:
        specie_names = [specie_names] # type: ignore
    df_species = pd.DataFrame(
        data=specie_names,
        columns=['english name', "scientific name"]
        )

    gen = []
    sp = []
    for name in df_species['scientific name']:
        gen.append(name.rpartition(' ')[0])
        sp.append(name.rpartition(' ')[2])

    df_query = pd.DataFrame()
    df_query['gen'] = gen
    df_query['sp'] = sp

    for key in info.keys():
        df_query[key] = f'{key}:{info[key]}'

    df_dataset = xc_multi_query(
        df_query=df_query,
        max_nb_files=max_nb_files,
        random_seed=random_seed,
        format_time=format_time,
        format_date=format_date,
        verbose=verbose
    )

    return df_dataset



#%%
# Path class
space =  '    '
branch = '│   '
# pointers:
tee =    '├── '
last =   '└── '

_CATALOG_LABEL = "ML Catalog Number"
_AUDIO_FORMATS = (".mp3", ".wav")


# Syllable = TypeVar('Syllable')
#%%
class ProjDirs:
    mg_param: PosixPath | Path
    images: PosixPath | Path
    examples: PosixPath | Path
    audios: PosixPath | Path
    spreadsheet: PosixPath | Path
    catalog: bool

    """
    Creates a ProjDirs class,  which is used to store a project's 
    file structure. This is required when constructing
    a :class:`~wavesongs.obj.Syllable` or a :class:`~wavesongs.obj.Song` 
    objects and generally useful to keep paths tidy and in the same
    location.

    Parameters
    ----------
        audios : str ='./assets/audio'
            Folder path where the audio records samples are stored.
        results: str = "./assets/results"
            Folder path to store the files and data generated.
        metadata: str = "spreadsheet.csv"
            Name of the csv file with the metadata of the audios. 
            Usually given by the data provider.

    Attributes
    ----------

    Example
    -------
        >>> proj_dirs = ProjDirs(
        >>>     "./assets/audio", "./assets/results", "spreadsheet.csv"
        >>> )
    """
    # %%
    def __init__(
        self,
        audios: str = "./assets/audios",
        results: str = "./assets/results",
        metadata: str = "spreadsheet.csv",
        catalog: bool = False
    ):
        """Constructor"""
        self.audios = Path(audios)
        self.results = Path(results)

        self.mg_param = self.results / "mg_params"
        self.images = self.results / "figures"
        self.examples = self.results / "audios"
        self.augmented_audios = self.examples / "augmented"

        self.spreadsheet = self.audios / metadata
        self.catalog = catalog

        # create folder in case they do not exist
        Path(self.results).mkdir(parents=True, exist_ok=True)
        Path(self.mg_param).mkdir(parents=True, exist_ok=True)
        Path(self.images).mkdir(parents=True, exist_ok=True)
        Path(self.examples).mkdir(parents=True, exist_ok=True)
        
        
        # Check if there is a metadata spreadsheet file inside audios folder
        spreadsheet_file = list(Path(self.audios).glob("*" + metadata))
        if len(spreadsheet_file) > 0 and self.catalog==True:
            self.catalog = True 
            self.catalog_label = _CATALOG_LABEL

        self.find_audios()
    
    # %%
    def find_audios(self, pretty=False) -> list | pd.DataFrame | None:
        """
        Search for all audios, mp3 and wav types, in the audios folder. 
        
        Parameters
        ----------
            None

        Return
        ------
            files_names : list
                List with the audios files names

        Notes
        -----
            If the audios folder contains a metadata file, spreadsheet.csv,
            the method will return a dataframe. However, the parameter
            `files_names` always is present.

        Example
        -------
            >>>
        """
        try:
            all_filles = Path(self.audios).glob("**/*")
            self.files = [a for a in all_filles if a.suffix in _AUDIO_FORMATS]
            self.files_names = [basename(f) for f in self.files]
            self.no_files = len(self.files_names)

            if self.catalog is True:
                self.data = pd.read_csv(self.spreadsheet, encoding_errors="ignore")
                self.data.dropna(axis=0, how="all", inplace=True)
                # self.data = data.convert_dtypes()
                self.data = self.data.astype({self.catalog_label: "str"})
                found_files = [
                    (
                        str(self.audios) + f"/{file}.mp3"
                        if file + ".mp3" in self.files_names
                        else str(self.audios) + f"/{file}.wav"
                    )
                    for file in self.data[self.catalog_label]
                ]
                self.data["File Path"] = found_files
                self.no_files = len(self.data)

                if pretty:
                    print(self.data)
                    return None
                else:
                    return self.data

            if pretty:
                print("Audios found:")
                for i in range(len(self.files_names)):
                    print(f"\t- {self.files_names[i]}")
                # print(self.data)
                return None
            else:
                return self.files_names
        
        except:
            raise Exception(f"The path {self.audios} does not contain any "+
                            "samples. Change the audios path and try again.")
    # %%
    def audios_info(self) -> None:
        """
        Get information about the audios folder: audios paths and 
        number of audios.

        Parameters
        ----------
            None

        Return
        ------
            None

        Example
        -------
            >>>
        """
        print(f"Audios path: {self.audios}\n")
        print("The folder has {} audio samples:".format(self.no_files))

        if self.catalog:
            print(self.data)
        else:
            for file in self.files_names:
                print("  - " + file)

    def find_audio(self, id: str) -> PosixPath | Path:
        """
        Find an audio in the audios folder by the id or filename

        Parameters
        ----------
            id : str
                Whole filename of a part of it. Usually, the catalog number. 

        Return
        ------
            path : PosixPath
                Aduio path location.

        Example
        -------
            >>>
        """
        if self.catalog:
            id_df = self.data.loc[self.data[self.catalog_label] == id]
            path = PosixPath(id_df["File Path"].values[0])
        else:
            path = [
                self.files[i]
                for i in range(len(self.files))
                if id in self.files_names[i]
            ][0]
        return path
    
    # %%
    # def import_mg(self, id, no_syllable=0):
    #     all_filles = Path(self.mg_param).glob("**/*")
    #     path_mg = [a for a in all_filles
    #             if f"-{no_syllable}-" in str(a) and id in str(a) and "mg." in str(a)][0]
        
    #     mg_df = pd.read_csv(path_mg, index_col=0)
    #     mg_df = mg_df.to_dict()["value"]

    #     t0 = float(mg_df["t_ini"])
    #     sr = int(mg_df["sr"])
    #     duration = float(mg_df["duration"])
    #     self.AUDIOS = mg_df["audios_folder"]
    #     params = eval(mg_df["params"])
        
    #     #self = ProjDirs(audios=audios_folder, results=self.results)
    #     synth = Syllable()
    #     # synth = Syllable(obj=self, duration=duration, sr=sr)
    #     synth.id = mg_df["id"]
    #     synth.type = mg_df["type"]
    #     synth.no_syllable = int(mg_df["no_syllable"])
    #     synth.metadata = mg_df["metadata"]
    #     synth.file_name = mg_df["file_name"]
    #     synth.z = eval(mg_df["z"])
    #     synth.t0_bs = t0
        
    #     if "curves_csv" in mg_df.keys():
    #         curves_df = pd.read_csv(mg_df["curves_csv"], index_col=0)
    #         time_s = curves_df["time"].to_numpy()
    #         alpha = curves_df["alpha"].to_numpy()
    #         beta = curves_df["beta"].to_numpy()
    #         duration = time_s[-1]
    #         curves = [alpha, beta]
    #         synth.alpha = alpha
    #         synth.beta = beta
    #     else:
    #         curves = alpha_beta(synth, synth.z, "fast")

        
    #     synth = motor_gestures(synth, curves, params)
    #     synth.acoustical_features(
    #         NN = int(mg_df["NN"]),
    #         ff_method = mg_df["ff_method"],
    #         umbral_FF = float(mg_df["umbral_FF"]),
    #         flim = [float(mg_df["f_ini"]), float(mg_df["f_end"])],
    #         Nt = int(mg_df["Nt"]),
    #         center = mg_df["center"],
    #         overlap = float(mg_df["overlap"]),
    #         llambda = float(mg_df["llambda"]),
    #         n_mfcc = int(mg_df["n_mfcc"]),
    #         n_mels = int(mg_df["n_mels"]),
    #         stft_window = mg_df["stft_window"]
    #     )
        
    #     return synth
    
    # def read_mg(
    #     self,
    #     file_name: str,
    #     no_syllable: Union[int, str],
    #     type: str = ""
    # ) -> Syllable:
    #     """
    #     Read motor gesture parameters from csv file
        
    #     Parameters
    #     ----------
    #         proj_dirs : ProjDirs

    #         file_name: str

    #         no_syllable: Union[int, str]

    #         type: str = ""

            
    #     Return
    #     -------
    #         synth: Syllable
        
    #     Example
    #     -------
    #         >>>
    #     """
    #     folder = self.mg_param # f"{results}/mg_param"
    #     file_name = f"{folder}/{file_name}-{no_syllable}-mg.csv" \
    #                     if type=="" \
    #                     else f"{folder}/{file_name}-{no_syllable}-{type}-mg.csv"
    #     df = pd.read_csv(file_name, index_col=0)

    #     data = df.to_dict()["value"]
    #     tlim = (float(data["t_ini"]), float(data["t_end"]))
    #     flim = (float(data["f_ini"]), float(data["f_end"]))
        
    #     z_json = data["z"].replace("'", "\"")
    #     z = json.loads(z_json)

    #     metadata_json = data["metadata"].replace("'", "\"")
    #     metadata = json.loads(metadata_json)
    #     root_folder = data["root_folder"] \
    #                     if data["root_folder"]!=".." \
    #                     else data["root_folder"]+"/"
    #     audios_folder = data["audios_folder"].replace(root_folder, "")

    #     proj_dirs = ProjDirs(audios=audios_folder)
    #     syllable = Syllable(
    #                 file_id=data["file_name"][:-4],
    #                 proj_dirs=proj_dirs,
    #                 tlim=tlim,
    #                 no_syllable=int(data["no_syllable"]), 
    #                 id=data["id"],
    #                 sr=int(data["sr"]),
    #                 metadata=metadata,
    #                 type=data["type"]
    #             )
    #     syllable.acoustical_features(
    #         flim=flim,
    #         umbral_FF=float(data["umbral_FF"]),
    #         NN=int(data["NN"]),
    #         ff_method=data["ff_method"]
    #     )
    #     syllable.z = z

    #     return syllable


    def tree_list(self, prefix: str=''):
        """A recursive generator, given a directory Path object
        will yield a visual tree structure line by line
        with each line prefixed by the same characters
        """
        dir_path = Path("./")
        contents = list(dir_path.iterdir())
        # contents each get pointers that are ├── with a final └── :
        pointers = [tee] * (len(contents) - 1) + [last]
        for pointer, path in zip(pointers, contents):
            yield prefix + pointer + path.name
            if path.is_dir(): # extend the prefix and recurse:
                extension = branch if pointer == tee else space 
                # i.e. space because last, └── , above so no more |
                yield from self.tree(prefix=prefix+extension)
        
    def tree(self, prefix: str='') -> str:
        tree_str = ""
        possibles = ["assets", "results", "audios", "figures", "mg_params"]
        for line in self.tree_list(prefix):
            count = 0
            for pos in possibles:
                if pos in line:
                    count += 1
            if count>=1:
                tree_str += line+"\n"
        print(tree_str)

        return tree_str
    
    def __str__(self):
        return f"""
    Audios: {self.audios}
    Results: {self.results}

        
    """