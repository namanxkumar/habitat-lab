# ---
# jupyter:
#   accelerator: GPU
#   jupytext:
#     cell_metadata_filter: -all
#     formats: nb_python//py:percent,colabs//ipynb
#     notebook_metadata_filter: all
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.3
#   kernelspec:
#     display_name: Python [conda env:habitat] *
#     language: python
#     name: conda-env-habitat-py
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.8.12
# ---

# %% [markdown]
# # Habitat 2.0 Gym API
# This tutorial covers how to use Habitat 2.0 environments as standard gym environments

# %%
# %%capture
# @title Install Dependencies (if on Colab) { display-mode: "form" }
# @markdown (double click to show code)

import os

if "COLAB_GPU" in os.environ:
    print("Setting up Habitat")
    # !curl -L https://raw.githubusercontent.com/facebookresearch/habitat-sim/main/examples/colab_utils/colab_install.sh | NIGHTLY=true bash -s
    # Setup to use the hab_suite branch of Habitat Lab.
    # ! cd /content/habitat-lab && git remote set-branches origin 'hab_suite' && git fetch -v && git checkout hab_suite && cd /content/habitat-lab && python setup.py develop --all && pip install . && cd -

# %%
import os

if "COLAB_GPU" in os.environ:
    print("Setting Habitat base path")
    # %env HABLAB_BASE_CFG_PATH=/content/habitat-lab
    import importlib

    import PIL

    importlib.reload(PIL.TiffTags)

# Video rendering utility.
from habitat_sim.utils import viz_utils as vut

# Quiet the Habitat simulator logging
os.environ["MAGNUM_LOG"] = "quiet"
os.environ["HABITAT_SIM_LOG"] = "quiet"


# If the import block below fails due to an error like "'PIL.TiffTags' has no attribute
# 'IFD'", then restart the Colab runtime instance and rerun this cell and the previous cell.

# %%
# The ONLY two lines you need to add to start importing Habitat 2.0 Gym environments.
import gym

import habitat_baselines.utils.gym_definitions

# %% [markdown]
# # Simple Example
# This example sets up the Pick task in render mode which includes a high resolution camera in the scene for visualization.

# %%
env = gym.make("HabitatGymRenderPick-v0")

video_file_path = "data/example_interact.mp4"
video_writer = vut.get_fast_video_writer(video_file_path, fps=30)

done = False
env.reset()
while not done:
    print("About to step")
    obs, reward, done, info = env.step(env.action_space.sample())
    print(reward)
    video_writer.append_data(env.render("rgb_array"))

video_writer.close()
if vut.is_notebook():
    vut.display_video(video_file_path)

# %% [markdown]
# # Environment Options
# To create the environment in performance mode remove `Render` from the environment ID string. The environment ID follows the format: `HabitatGym[Render?][Task Name]-v0`. All the supported environment IDs are listed below. The `Render` option can always be included.
#
# * `HabitatGymCloseCab-v0`
# * `HabitatGymCloseFridge-v0`
# * `HabitatGymNavToObj-v0`
# * `HabitatGymOpenCab-v0`
# * `HabitatGymPick-v0`
# * `HabitatGymPlace-v0`
# * `HabitatGymReachState-v0`
#
# The Gym environments are automatically registered from the RL training configurations under ["habitat_baselines/config/rearrange"](https://github.com/facebookresearch/habitat-lab/tree/hab_suite_dev/habitat_baselines/config/rearrange). The `GYM_AUTO_NAME` key in the YAML file determines the `[Task Name]`. The observation keys in `RL.GYM_OBS_KEYS` are what is returned in the observation space. If the the observations are a set of 1D arrays, then the observation space is automatically flattened. For example, in `HabitatGymReachState-v0` the observation space is `RL.GYM_OBS_KEYS = ['joint', 'relative_resting_position']`. `joint` is a 7D array and `relative_resting_position` is a 3D array. These two arrays are concatenated automatically to give a `10D` observation space. On the other hand, in environments with image observations, the observation is returned as a dictionary.
#
# An example of these different observation spaces is demonstrated below:

# %%
# Dictionary observation space
env = gym.make("HabitatGymPick-v0")
print({k: v.shape for k, v in env.observation_space.spaces.items()})

# Array observation space
env = gym.make("HabitatGymReachState-v0")
print(env.observation_space)

# %% [markdown]
# # Environment Configuration
#
# You can also modify the config specified in the YAML file through `gym.make` by passing the `override_options` argument. Here is an example of changing the gripper type to use the suction grasp in the Pick Task.

# %%
env = gym.make(
    "HabitatGymPick-v0",
    override_options=[
        "TASK_CONFIG.TASK.ACTIONS.ARM_ACTION.GRIP_CONTROLLER",
        "SuctionGraspAction",
    ],
)
