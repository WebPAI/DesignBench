from enum import Enum


class Framework(str, Enum):
    VANILLA = "vanilla"
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"


class Task(str, Enum):
    REPAIR = "repair"
    GENERATION = "generation"
    EDIT = "edit"
    COMPILE = "compile"


class Mode(str, Enum):
    CODE = "code"
    IMAGE = "image"
    BOTH = "both"
    MARK = "mark"
