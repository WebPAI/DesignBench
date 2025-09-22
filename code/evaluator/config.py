from enum import Enum


DesignBench_Path = "/Home/User/DesignBench/"

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



key_path = DesignBench_Path + "code/prompting/key.json"

folder_dic = {
    Task.GENERATION: DesignBench_Path + "data/DesignGeneration/",
    Task.EDIT: DesignBench_Path + "data/DesignEdit/",
    Task.REPAIR: DesignBench_Path + "data/DesignRepair/",
}

deploy_link_dic = {
    Framework.VUE: "http://localhost:5173/",  # npm run dev
    Framework.REACT: "http://localhost:3000/",  # npm run dev
    Framework.ANGULAR: "http://localhost:4200/",  # ng serve
}

project_code_path_dic = {
    Framework.VUE: DesignBench_Path + "web/my-vue-app/src/components/HelloWorld.vue",
    Framework.REACT: DesignBench_Path + "web/my-react-app/app/page.tsx",
    Framework.ANGULAR: DesignBench_Path + "web/my-angular-app/src/app/new.component.html"
    # "angular": {
    #     "html": DesignBench_Path + "web/my-angular-app/app/new.component.html",
    #     "ts": DesignBench_Path + "web/my-angular-app/app/new.component.ts"
    # }
}

format_dic = {
    Framework.VUE: "vue",
    Framework.REACT: "jsx",
    Framework.VANILLA: "html",
    Framework.ANGULAR: "angular"
}
