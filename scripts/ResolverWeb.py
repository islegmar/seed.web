#!/usr/bin/python
# -------------------------------------------
# Base Resolver for the Web part
# -------------------------------------------
from ResolverWebrad import ResolverWebrad

class ResolverWeb(ResolverWebrad):
  def __init__(self, moduleName, cfgModule, options):
    ResolverWebrad.__init__(self, moduleName, cfgModule, options)

  # ============================================================================
  # Test functions for conditional contents
  # ============================================================================
  def printTestOutputBreadrumb(self):
    return ""  