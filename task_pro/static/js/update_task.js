const recordBtn = document.getElementById('recordBtn');
const stopBtn = document.getElementById('stopBtn');
const audioPreview = document.getElementById('audioPreview');
const reRecordBtn = document.getElementById('reRecordBtn');
const recordingTime = document.getElementById('recordingTime');

let mediaRecorder;
let audioChunks = [];
let recordedAudioBlob = null; 
let startTime;

// Handle recording
recordBtn.addEventListener('click', async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();
    recordBtn.classList.add('hidden');
    stopBtn.classList.remove('hidden');
    recordingTime.textContent = "00:00";
    recordingTime.classList.remove('hidden');
    audioChunks = [];

    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
        recordedAudioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const audioUrl = URL.createObjectURL(recordedAudioBlob);
        audioPreview.src = audioUrl;
        audioPreview.classList.remove('hidden');
        reRecordBtn.classList.remove('hidden');
        stopBtn.classList.add('hidden');
        recordingTime.classList.add('hidden');
    };

    startTime = Date.now();
    updateRecordingTime();
});

// Stop recording
stopBtn.addEventListener('click', () => {
    if (mediaRecorder) {
        mediaRecorder.stop();
    }
});

// Update recording timer
function updateRecordingTime() {
    const interval = setInterval(() => {
        if (!mediaRecorder || mediaRecorder.state === 'inactive') {
            clearInterval(interval);
            return;
        }
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        recordingTime.textContent = new Date(elapsed * 1000).toISOString().substr(11, 8);
    }, 1000);
}

// Handle re-recording
reRecordBtn.addEventListener('click', () => {
    audioPreview.src = ""; // Clear the existing audio
    audioPreview.classList.add('hidden');
    reRecordBtn.classList.add('hidden');
    recordBtn.classList.remove('hidden');
    recordedAudioBlob = null; // Clear the recorded blob
});

const statusField = document.querySelector('.status_selection'); // Ensure this matches your select element's class
const Depend_on_drop_down = document.querySelector('.Depend_on_div'); // Ensure this matches your dropdown container's class
const selected_user_ = document.querySelector('#selected_user');


// Add an event listener to monitor changes in the status field
statusField.addEventListener('change', function () {
    if (statusField.value === 'Stuck') {
        Depend_on_drop_down.style.display = 'block';
        console.log("done")
    } else {
        Depend_on_drop_down.style.display = 'none';
        console.log('not done')
    }
});


// Set the initial state when the page loads
if (statusField.value === 'Stuck') {
    Depend_on_drop_down.style.display = 'block';
} else {
    Depend_on_drop_down.style.display = 'none';
    console.log('hii')
}



const task_select = document.querySelector('#task_selection')

selected_user_.addEventListener('change', function() {
    const user_id = this.value;

    if (!user_id){
        task_select.innerHTML = '<option value="">Select Task'
        return;
    }

    fetch('/get-tasks-for-user/' + user_id + '/',{
        method:'GET',
        headers:{
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data =>{
        const task_selection = document.getElementById('task_selection');
        task_selection.innerHTML = '<option value="">Select Task</option>';

        if (data.user_tasks.length > 0){
            data.user_tasks.forEach(task=>{
                const option = document.createElement('option');
                option.value = task.id;
                option.textContent = task.title;
                task_selection.appendChild(option);
            });
        }else{
            const option = document.createElement('option');
            option.value = "";
            option.textContent = "NO Task Available";
            task_selection.appendChild(option);
        }
    })
    .catch(error =>{
        console.error('Error fetching tasks ',error);
    });

});


// for waiting user
const waiting_user = document.getElementsByClassName('waiting_user')
console.log(waiting_user)
Array.from(waiting_user).forEach(waiting=>{
    if(waiting.innerHTML){
        fetch('waiting_user/'+ waiting.innerHTML+'/',{
            method :'GET',  
            headers:{
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data =>{
            if(data){
                waiting.innerHTML = data.user_data[0].name;
            }else{
                waiting.innerHTML = ''
            }
        })
        .catch(error=>{
            console.error('Error fetching ',error);
        });
    }
})