const api = window.FitLogAPI

if (!api.token) {
    window.location.href = '/'
}

document.addEventListener('DOMContentLoaded', async function() {
    await loadDashboardData()
    setupEventListeners()
})

async function loadDashboardData() {
    try {
        const user = await api.getCurrentUser()
        if (!user) {
            api.logout()
            return
        }
        
        document.getElementById('welcomeText').textContent = 
            `Добро пожаловать, ${user.full_name || user.username}!`
        document.getElementById('userEmail').textContent = user.email
        document.getElementById('currentUserEmail').textContent = user.email
        
        await loadStats()
        await loadWorkouts()
        await loadGoals()
        
    } catch (error) {
        showNotification('Ошибка загрузки данных', 'error')
    }
}

async function loadStats() {
    try {
        const stats = await api.request('/stats/dashboard')
        updateStatsUI(stats)
    } catch (error) {
        document.getElementById('statsGrid').innerHTML = `
            <div class="empty-state">
                <i class="fas fa-chart-line"></i>
                <p>Не удалось загрузить статистику</p>
            </div>
        `
    }
}

function updateStatsUI(stats) {
    const statsGrid = document.getElementById('statsGrid')
    
    if (!stats) {
        statsGrid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-chart-line"></i>
                <p>Нет данных</p>
            </div>
        `
        return
    }
    
    statsGrid.innerHTML = `
        <div class="stat-card">
            <div class="stat-icon"><i class="fas fa-dumbbell"></i></div>
            <div class="stat-value">${stats.workouts?.weekly || 0}</div>
            <div class="stat-label">Тренировок за неделю</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon"><i class="fas fa-chart-line"></i></div>
            <div class="stat-value">${stats.workouts?.avg_per_week || 0}</div>
            <div class="stat-label">Среднее в неделю</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon"><i class="fas fa-utensils"></i></div>
            <div class="stat-value">${Math.round(stats.nutrition?.avg_daily_calories || 0)}</div>
            <div class="stat-label">Ккал/день</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon"><i class="fas fa-bullseye"></i></div>
            <div class="stat-value">${stats.goals?.active || 0}</div>
            <div class="stat-label">Активных целей</div>
        </div>
    `
}

async function loadWorkouts() {
    try {
        const workouts = await api.request('/workouts/?limit=5')
        updateWorkoutsUI(workouts)
    } catch (error) {
        document.getElementById('workoutsList').innerHTML = `
            <div class="empty-state">
                <i class="fas fa-dumbbell"></i>
                <p>Не удалось загрузить тренировки</p>
            </div>
        `
    }
}

function updateWorkoutsUI(workouts) {
    const workoutsList = document.getElementById('workoutsList')
    
    if (!workouts || workouts.length === 0) {
        workoutsList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-dumbbell"></i>
                <p>Нет тренировок</p>
                <button class="btn-primary" onclick="showWorkoutModal()">Добавить тренировку</button>
            </div>
        `
        return
    }
    
    workoutsList.innerHTML = workouts.map(workout => `
        <div class="workout-card">
            <div class="workout-header">
                <div class="workout-name">${workout.name}</div>
                <div class="workout-date">${new Date(workout.date).toLocaleDateString('ru-RU')}</div>
            </div>
            <div class="workout-details">
                <span><i class="fas fa-clock"></i> ${workout.duration || 0} мин</span>
                <span><i class="fas fa-list"></i> ${workout.exercises?.length || 0} упражнений</span>
            </div>
            ${workout.notes ? `<p style="color: #666; font-size: 14px; margin-top: 10px;">${workout.notes}</p>` : ''}
        </div>
    `).join('')
}

async function loadGoals() {
    try {
        const goals = await api.request('/goals/')
        const activeGoals = goals.filter(g => !g.is_completed)
        updateGoalsUI(activeGoals)
    } catch (error) {
        document.getElementById('goalsList').innerHTML = `
            <div class="empty-state">
                <i class="fas fa-bullseye"></i>
                <p>Не удалось загрузить цели</p>
            </div>
        `
    }
}

function updateGoalsUI(goals) {
    const goalsList = document.getElementById('goalsList')
    
    if (!goals || goals.length === 0) {
        goalsList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-bullseye"></i>
                <p>Нет целей</p>
                <button class="btn-primary" onclick="showGoalModal()">Поставить цель</button>
            </div>
        `
        return
    }
    
    goalsList.innerHTML = goals.map(goal => {
        const progress = goal.target_value ? (goal.current_value / goal.target_value) * 100 : 0
        return `
            <div class="goal-card">
                <div class="goal-header">
                    <div class="goal-title">${goal.title}</div>
                    <div class="goal-progress">${goal.current_value}/${goal.target_value} ${goal.unit}</div>
                </div>
                ${goal.description ? `<p style="color: #666; font-size: 14px; margin-bottom: 10px;">${goal.description}</p>` : ''}
                <div class="goal-progress-bar">
                    <div class="goal-progress-fill" style="width: ${Math.min(progress, 100)}%"></div>
                </div>
                ${goal.deadline ? `<div style="color: #666; font-size: 14px; margin-top: 10px;">
                    <i class="fas fa-calendar"></i> До ${new Date(goal.deadline).toLocaleDateString('ru-RU')}
                </div>` : ''}
            </div>
        `
    }).join('')
}

function setupEventListeners() {
    document.getElementById('logoutBtn').addEventListener('click', () => {
        api.logout()
    })
    
    document.getElementById('addWorkoutBtn').addEventListener('click', showWorkoutModal)
    document.getElementById('addGoalBtn').addEventListener('click', showGoalModal)
    document.getElementById('quickWorkoutBtn').addEventListener('click', showQuickWorkoutModal)
    document.getElementById('addMealBtn').addEventListener('click', showMealModal)
    document.getElementById('addMeasurementBtn').addEventListener('click', showMeasurementModal)
    
    document.getElementById('quickWorkoutModalOverlay').addEventListener('click', closeQuickWorkoutModal)
    document.getElementById('mealModalOverlay').addEventListener('click', closeMealModal)
    document.getElementById('measurementModalOverlay').addEventListener('click', closeMeasurementModal)
    document.getElementById('workoutModalOverlay').addEventListener('click', closeWorkoutModal)
    document.getElementById('goalModalOverlay').addEventListener('click', closeGoalModal)
}

let exerciseCounter = 0

function showWorkoutModal() {
    document.getElementById('workoutModalOverlay').style.display = 'block'
    document.getElementById('workoutModal').style.display = 'block'
    document.body.style.overflow = 'hidden'
    
    document.getElementById('workoutDate').value = new Date().toISOString().split('T')[0]
    exerciseCounter = 0
    document.getElementById('exercisesContainer').innerHTML = ''
    addExercise()
}

function closeWorkoutModal() {
    document.getElementById('workoutModalOverlay').style.display = 'none'
    document.getElementById('workoutModal').style.display = 'none'
    document.body.style.overflow = 'auto'
}

function showGoalModal() {
    document.getElementById('goalModalOverlay').style.display = 'block'
    document.getElementById('goalModal').style.display = 'block'
    document.body.style.overflow = 'hidden'
    
    document.getElementById('goalDeadline').value = ''
    document.getElementById('currentValue').value = '0'
}

function closeGoalModal() {
    document.getElementById('goalModalOverlay').style.display = 'none'
    document.getElementById('goalModal').style.display = 'none'
    document.body.style.overflow = 'auto'
}

function showQuickWorkoutModal() {
    document.getElementById('quickWorkoutModalOverlay').style.display = 'block'
    document.getElementById('quickWorkoutModal').style.display = 'block'
    document.body.style.overflow = 'hidden'
}

function closeQuickWorkoutModal() {
    document.getElementById('quickWorkoutModalOverlay').style.display = 'none'
    document.getElementById('quickWorkoutModal').style.display = 'none'
    document.body.style.overflow = 'auto'
}

function showMealModal() {
    document.getElementById('mealModalOverlay').style.display = 'block'
    document.getElementById('mealModal').style.display = 'block'
    document.body.style.overflow = 'hidden'
    document.getElementById('mealTime').value = new Date().toTimeString().substring(0,5)
}

function closeMealModal() {
    document.getElementById('mealModalOverlay').style.display = 'none'
    document.getElementById('mealModal').style.display = 'none'
    document.body.style.overflow = 'auto'
}

function showMeasurementModal() {
    document.getElementById('measurementModalOverlay').style.display = 'block'
    document.getElementById('measurementModal').style.display = 'block'
    document.body.style.overflow = 'hidden'
    document.getElementById('measurementDate').value = new Date().toISOString().split('T')[0]
}

function closeMeasurementModal() {
    document.getElementById('measurementModalOverlay').style.display = 'none'
    document.getElementById('measurementModal').style.display = 'none'
    document.body.style.overflow = 'auto'
}

function addExercise() {
    exerciseCounter++
    const exerciseId = `exercise-${exerciseCounter}`

    const exerciseHTML = `
        <div class="exercise-item" id="${exerciseId}">
            <div class="exercise-header">
                <h4 style="margin: 0;">Упражнение ${exerciseCounter}</h4>
                <button type="button" class="remove-exercise" onclick="removeExercise('${exerciseId}')">
                    <i class="fas fa-times"></i> Удалить
                </button>
            </div>
            
            <div class="form-group">
                <input type="text" class="exercise-name" placeholder="Название" required>
            </div>
            
            <div class="form-group">
                <select class="exercise-category">
                    <option value="">Категория</option>
                    <option value="chest">Грудь</option>
                    <option value="back">Спина</option>
                    <option value="legs">Ноги</option>
                    <option value="shoulders">Плечи</option>
                    <option value="arms">Руки</option>
                    <option value="core">Пресс</option>
                    <option value="cardio">Кардио</option>
                </select>
            </div>
            
            <div class="sets-section">
                <h5>Подходы</h5>
                <div class="sets-container" id="sets-${exerciseId}"></div>
                <button type="button" class="btn-secondary" onclick="addSet('${exerciseId}')" style="margin-top: 10px; padding: 8px 12px;">
                    <i class="fas fa-plus"></i> Добавить подход
                </button>
            </div>
        </div>
    `

    document.getElementById('exercisesContainer').insertAdjacentHTML('beforeend', exerciseHTML)
    addSet(exerciseId)
}

function removeExercise(exerciseId) {
    document.getElementById(exerciseId).remove()
    updateExerciseNumbers()
}

function updateExerciseNumbers() {
    const exercises = document.querySelectorAll('.exercise-item')
    exercises.forEach((exercise, index) => {
        const header = exercise.querySelector('h4')
        if (header) {
            header.textContent = `Упражнение ${index + 1}`
        }
    })
}

function addSet(exerciseId) {
    const setsContainer = document.getElementById(`sets-${exerciseId}`)
    if (!setsContainer) return

    const setNumber = setsContainer.children.length + 1

    const setHTML = `
        <div class="set-item">
            <label>Подход ${setNumber}</label>
            <input type="number" class="set-reps" placeholder="Повторения" min="1">
            <input type="number" class="set-weight" placeholder="Вес (кг)" step="0.5">
            <input type="number" class="set-rest" placeholder="Отдых (сек)" min="0">
        </div>
    `

    setsContainer.insertAdjacentHTML('beforeend', setHTML)
}

document.getElementById('addWorkoutForm').addEventListener('submit', async function(e) {
    e.preventDefault()

    const workoutData = {
        name: document.getElementById('workoutName').value,
        date: document.getElementById('workoutDate').value,
        duration: parseInt(document.getElementById('workoutDuration').value) || null,
        notes: document.getElementById('workoutNotes').value || '',
        exercises: []
    }

    document.querySelectorAll('.exercise-item').forEach(exercise => {
        const exerciseData = {
            name: exercise.querySelector('.exercise-name').value,
            category: exercise.querySelector('.exercise-category').value || null,
            sets: []
        }
        
        const setsContainer = exercise.querySelector('.sets-container')
        if (setsContainer) {
            setsContainer.querySelectorAll('.set-item').forEach((set, index) => {
                exerciseData.sets.push({
                    set_number: index + 1,
                    reps: parseInt(set.querySelector('.set-reps').value) || null,
                    weight: parseFloat(set.querySelector('.set-weight').value) || null,
                    rest_time: parseInt(set.querySelector('.set-rest').value) || null,
                    completed: true
                })
            })
        }
        
        if (exerciseData.name) {
            workoutData.exercises.push(exerciseData)
        }
    })

    try {
        const submitBtn = this.querySelector('button[type="submit"]')
        submitBtn.disabled = true
        submitBtn.textContent = 'Сохранение...'
        
        await api.request('/workouts/', {
            method: 'POST',
            body: JSON.stringify(workoutData)
        })
        
        showNotification('Тренировка сохранена', 'success')
        closeWorkoutModal()
        await loadWorkouts()
        await loadStats()
        
    } catch (error) {
        showNotification(error.message || 'Ошибка сохранения', 'error')
    } finally {
        const submitBtn = this.querySelector('button[type="submit"]')
        submitBtn.disabled = false
        submitBtn.textContent = 'Сохранить тренировку'
    }
})

document.getElementById('addGoalForm').addEventListener('submit', async function(e) {
    e.preventDefault()

    const goalData = {
        title: document.getElementById('goalTitle').value,
        description: document.getElementById('goalDescription').value || '',
        goal_type: document.getElementById('goalType').value,
        target_value: parseFloat(document.getElementById('targetValue').value),
        current_value: parseFloat(document.getElementById('currentValue').value) || 0,
        unit: document.getElementById('goalUnit').value,
        deadline: document.getElementById('goalDeadline').value || null
    }

    try {
        const submitBtn = this.querySelector('button[type="submit"]')
        submitBtn.disabled = true
        submitBtn.textContent = 'Сохранение...'
        
        await api.request('/goals/', {
            method: 'POST',
            body: JSON.stringify(goalData)
        })
        
        showNotification('Цель сохранена', 'success')
        closeGoalModal()
        await loadGoals()
        await loadStats()
        
    } catch (error) {
        showNotification(error.message || 'Ошибка сохранения', 'error')
    } finally {
        const submitBtn = this.querySelector('button[type="submit"]')
        submitBtn.disabled = false
        submitBtn.textContent = 'Сохранить цель'
    }
})

document.getElementById('quickWorkoutForm').addEventListener('submit', async function(e) {
    e.preventDefault()
    
    const workoutData = {
        name: document.getElementById('quickWorkoutName').value,
        date: new Date().toISOString().split('T')[0],
        duration: parseInt(document.getElementById('quickDuration').value) || 30,
        notes: document.getElementById('quickNotes').value || ''
    }
    
    try {
        const submitBtn = this.querySelector('button[type="submit"]')
        submitBtn.disabled = true
        submitBtn.textContent = 'Сохранение...'
        
        await api.request('/workouts/', {
            method: 'POST',
            body: JSON.stringify(workoutData)
        })
        
        showNotification('Тренировка сохранена', 'success')
        closeQuickWorkoutModal()
        await loadWorkouts()
        await loadStats()
        
    } catch (error) {
        showNotification(error.message || 'Ошибка сохранения', 'error')
    } finally {
        const submitBtn = this.querySelector('button[type="submit"]')
        submitBtn.disabled = false
        submitBtn.textContent = 'Сохранить'
    }
})

document.getElementById('addMealForm').addEventListener('submit', async function(e) {
    e.preventDefault()
    
    const mealData = {
        name: document.getElementById('mealName').value,
        meal_type: document.getElementById('mealType').value,
        date: new Date().toISOString().split('T')[0],
        time: new Date().toISOString().split('T')[0] + 'T' + document.getElementById('mealTime').value + ':00',
        calories: parseFloat(document.getElementById('mealCalories').value) || null,
        protein: parseFloat(document.getElementById('mealProtein').value) || null,
        carbs: parseFloat(document.getElementById('mealCarbs').value) || null,
        fat: parseFloat(document.getElementById('mealFat').value) || null
    }
    
    try {
        const submitBtn = this.querySelector('button[type="submit"]')
        submitBtn.disabled = true
        submitBtn.textContent = 'Сохранение...'
        
        await api.request('/meals/', {
            method: 'POST',
            body: JSON.stringify(mealData)
        })
        
        showNotification('Прием пищи сохранен', 'success')
        closeMealModal()
        await loadStats()
        
    } catch (error) {
        showNotification(error.message || 'Ошибка сохранения', 'error')
    } finally {
        const submitBtn = this.querySelector('button[type="submit"]')
        submitBtn.disabled = false
        submitBtn.textContent = 'Сохранить'
    }
})

document.getElementById('addMeasurementForm').addEventListener('submit', async function(e) {
    e.preventDefault()
    
    const measurementData = {
        date: document.getElementById('measurementDate').value,
        weight: parseFloat(document.getElementById('measurementWeight').value) || null,
        body_fat: parseFloat(document.getElementById('measurementFat').value) || null,
        chest: parseFloat(document.getElementById('measurementChest').value) || null,
        waist: parseFloat(document.getElementById('measurementWaist').value) || null,
        hips: parseFloat(document.getElementById('measurementHips').value) || null,
        neck: parseFloat(document.getElementById('measurementNeck').value) || null
    }
    
    try {
        const submitBtn = this.querySelector('button[type="submit"]')
        submitBtn.disabled = true
        submitBtn.textContent = 'Сохранение...'
        
        await api.request('/measurements/', {
            method: 'POST',
            body: JSON.stringify(measurementData)
        })
        
        showNotification('Измерения сохранены', 'success')
        closeMeasurementModal()
        await loadStats()
        
    } catch (error) {
        showNotification(error.message || 'Ошибка сохранения', 'error')
    } finally {
        const submitBtn = this.querySelector('button[type="submit"]')
        submitBtn.disabled = false
        submitBtn.textContent = 'Сохранить'
    }
})

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeWorkoutModal()
        closeGoalModal()
        closeQuickWorkoutModal()
        closeMealModal()
        closeMeasurementModal()
    }
})