# 项目目录结构设计

```text
/
├── AGENTS.md                          # 开发约定
├── README.md                          # 项目介绍
├── .gitattributes                     # Git 属性配置
│
├── docs/                              # 全局项目文档。具体端的文档放具体的里，如关于后台的设计，放 backend/docs/designs
│   ├── standards/                     # 开发规范
│   ├── designs/                       # 设计文档（包含全局概念定义）
│   ├── gotchas/                       # 易错点介绍
│   └── todo-list.md                   # 待办事项
│
├── backend/
├── frontend/
│
├── scripts/                           # 项目级开发与管理脚本
├── deployment/                        # 部署资源
└── devops/                            # 运维脚本与个人运维工具
```

## backend/

详情请看[后台目录结构设计](../../backend/docs/standards/project_structure.md)

## frontend/

详情请看[前端目录结构设计](../../frontend/docs/standards/project_structure.md)
