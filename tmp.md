# Scheduler
get ready task and assign to simulation

# APIs for web
## JSON format
```
{
    code: uint32,
    data: {},
    message: string
}
```

## TaskState
- Queued = 0
- Running = 1
- Cancel = 2
- Success = 3
- Failed = 4

## getTaskStatus: /api/task/status
### params:
- task_id: uint64
### result: list
- state: uint 
- timestamp: string 
### example
- req: /api/task/status?task_id=1
- res:
```
{
    code: 0,
    data: 
    [
        {
            state: 0,
            timestamp: "2016-04-09 14:00:00"
        },
        {
            state: 1,
            timestamp: "2016-04-09 14:00:03"
        }
    ],
    message: null
}
```

## getTaskListStatus: /api/task/list/status
### params:
- task_ids: uint64 split by ','
### result: map<task_id>
- state: uint 
- disk_size: uint64
- cost: uint64
### example
- req: /api/task/list/status?task_ids=1,2
- res:
```
{
    code: 0,
    data: 
    {
        "1": 
            {
                state: 0,
                disk_size: 0,
                cost: 0
            },
        "2": 
            {
                state: 3,
                disk_size: 100,
                cost: 4
            }
    },
    message: null
}
```

## getCompanyBalance: /api/company/balance
### params:
- corp_id: uint64
### result: uint64
### example
- req: /api/company/balance?corp_id=1
- res:
```
{
    code: 0,
    data: 1000,
    message: null
}
```

## cancelTask: /api/task/cancel
### params:
- task_id: uint64
- corp_id: uint64
### result: null
### example
- req: /api/task/cancel?task_id=1&corp_id=1
- res:
```
{
    code: 0,
    data: null,
    message: null
}
```