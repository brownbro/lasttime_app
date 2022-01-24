const backend_url = '$BACKEND_URL'

const vm = new Vue({
    el: '#tasks',
    data: function() {
        return {
            tasks: [],
            name: "",
        }
    },
    async mounted() {
        const data = await fetch(backend_url + "/tasks")
        const json = await data.json()
        const tasks = json.tasks
        const now = Date.now()
        const ms_in_a_day = 24 * 60 * 60 * 1000
        tasks.forEach(function(task){
            task.days_from = ~~((now - Date.parse(task.last_time)) / ms_in_a_day)
        })
        this.tasks = tasks
    },
    methods: {
        onDone: function(task_id) {
            let url = new URL(backend_url + "/tasks/" + task_id + "/done")

            fetch(url, {
                method: "PUT",
            })
            .then(response => response.json())
            .then(data => {
                console.log(data.task)
                this.tasks.forEach(function(task){
                    if (task.id === data.task.id) {
                        task.days_from = 0
                        task.last_time = data.task.done_dates.slice(-1)[0]
                    }
                })
            })
        },
        onDelete: function(task_id) {
            let url = new URL(backend_url + "/tasks/" + task_id)

            fetch(url, {
                method: "Delete",
            })
            .then(response => response.json())
            .then(data => {
                this.tasks = this.tasks.filter((task) => {
                    return task.id != task_id
                })
            })
        },
        onCreate: function() {
            let url = new URL(backend_url + "/tasks")
            const requestOptions = {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: this.name })
            };

            fetch(url, requestOptions)
            .then(response => response.json())
            .then(data => {
                const new_task = data.task
                console.log(new_task)
                new_task.days_from = 0
                new_task.last_time = new_task.done_dates[0]
                this.tasks.push(new_task)
                this.name = ""
            })
        }
    }
})

Vue.component('task', {
    props: ['task'],
    template: `
        <div>
            <h4>{{ task.name }}</h4>
            <p>{{ task.days_from }}日 ({{ task.last_time }})
            <button class="btn btn-primary" v-on:click="$emit('done', task.id)">更新</button>
            <button class="btn btn-danger" v-on:click="$emit('delete', task.id)">削除</button> </p>
        </div>
        `,
})