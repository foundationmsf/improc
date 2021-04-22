# coding: utf8
# benchmark_tools.interfaces

# Copyright 2019 Fondation Medecins Sans Frontières https://fondation.msf.fr/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This file is part of the ASTapp image processing library
# Author: Marco Pascucci

from .usecases import creteil, creteil_es_test, amman, amman_blood_agar, whonet_nada
from . import astscript

__doc__ = "This module contains abstract classes and implementations to easily " \
          "access AST annotations for benchmarking."
