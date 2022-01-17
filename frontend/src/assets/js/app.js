const vm = new Vue({
    el: '#tasks',
    data: function() {
        return {
            tasks: []
        }
    },
    async mounted() {
        const data = await fetch("http://localhost:8081/api/tasks")
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
        onDoneTask: function(task_id) {
            let url = new URL("http://localhost:8081/api/tasks/" + task_id + "/done")

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
        }
    }
})

Vue.component('task', {
    props: ['task'],
    template: `
        <div>
            <h4>{{ task.name }}</h4>
            <p>{{ task.days_from }}日 ({{ task.last_time }})
            <button v-on:click="$emit('done-task', task.id)">更新</button> </p>
        </div>
        `,
})