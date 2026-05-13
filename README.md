# GetFitX — Smart Calorie Tracking Web App

## Overview

GetFitX is a full stack health-tech web application focused on:

- Smart calorie tracking
- Weight loss management
- Calorie deficit monitoring
- Progress visualization
- Streak systems
- Habit consistency
- Gamification

The primary goal of Phase 1 is to build a strong MVP (Minimum Viable Product) with manual calorie tracking and intelligent analytics before integrating AI-powered features in later phases.

---

# Tech Stack

## Frontend
- React.js
- Tailwind CSS
- Recharts
- Framer Motion
- Axios
- React Router DOM

## Backend
- Python Flask
- Flask JWT Authentication
- Flask CORS
- PyMongo

## Database
- MongoDB Atlas

## Deployment
- Vercel (Frontend)
- Render (Backend)

---

# Core Features — Phase 1

## 1. Authentication System

### Pages
- Home Page
- Signup Page
- Login Page

### User Signup Details
- Name
- Email
- Password
- Age
- Gender
- Height
- Current Weight
- Goal Weight
- Activity Level
- Goal Deadline

### Authentication Features
- JWT Authentication
- Password Hashing
- Protected Routes
- Persistent Login

---

# 2. Smart Calorie Target System

The application calculates:

- BMR
- TDEE
- Daily Calorie Target
- Required Daily Deficit

---

## BMR Formula

### Male

```math
BMR = 10W + 6.25H - 5A + 5
```

### Female

```math
BMR = 10W + 6.25H - 5A - 161
```

Where:
- W = Weight (kg)
- H = Height (cm)
- A = Age

---

## TDEE Formula

```math
TDEE = BMR × ActivityFactor
```

---

## Weight Loss Formula

```math
TotalDeficit = WeightLoss × 7700
```

---

## Daily Deficit Formula

```math
DailyDeficit = TotalDeficit / DaysRemaining
```

---

## Daily Target Formula

```math
DailyTarget = TDEE - DailyDeficit
```

---

# 3. Dashboard System

The dashboard acts as the main console of the application.

## Dashboard Features

### Daily Summary Cards
- Daily Calorie Target
- Calories Consumed
- Remaining Calories
- Daily Deficit
- Weekly Deficit
- Monthly Deficit

---

## Food Entry System

### Inputs
- Food Name
- Calories
- Quantity
- Meal Type

### Meal Types
- Breakfast
- Lunch
- Dinner
- Snacks

### Features
- Add Food
- Edit Food
- Delete Food
- Auto Calorie Summation

---

## Progress Ring

A circular progress indicator showing:
- Daily calorie consumption percentage
- Remaining calories

### Color Logic
- Green → Within target
- Yellow → Near limit
- Red → Exceeded target

---

# 4. Weight Logging System

Users can:
- Add daily weight
- Add weekly weight

## Features
- Weight trend graph
- Progress comparison
- Expected vs actual progress

---

# 5. Analytics System

## Graphs Included

### Daily Calorie Graph
- Line chart

### Weekly Deficit Graph
- Bar chart

### Weight Trend Graph
- Smooth line graph

### Goal Prediction Card
Example:
“At your current pace, you may reach your goal in 84 days.”

---

# 6. Streak System

Inspired by GitHub and LeetCode contribution systems.

## Features
- Daily tracking streak
- Longest streak
- Heatmap calendar
- Consistency tracking

---

## Heatmap Color Logic

- Light Green → Small deficit
- Dark Green → Excellent deficit
- Yellow → Near target
- Red → Overeating

---

# 7. Smart Insights Engine

The backend analyzes user behavior and generates insights.

## Example Insights

- “Your average deficit this week is 540 kcal.”
- “Sunday is your highest calorie day.”
- “You are improving consistency.”

---

# 8. Habit Tracker

Daily habits include:

- Water Intake
- Workout Completed
- Sleep Completed

---

# 9. Achievement System

## Example Badges

- First Food Log
- 7 Day Streak
- 10,000 kcal Deficit
- First 1kg Lost
- 30 Day Streak

---

# Database Design

## Collections

```text
users
daily_logs
weight_logs
streaks
habits
achievements
insights
```

---

# Frontend Structure

```text
src/
│
├── components/
├── pages/
├── layouts/
├── context/
├── hooks/
├── services/
├── charts/
├── animations/
├── utils/
└── App.jsx
```

---

# Backend Structure

```text
backend/
│
├── app.py
├── config/
├── models/
├── routes/
├── controllers/
├── services/
├── middleware/
├── utils/
└── requirements.txt
```

---

# Backend API Routes

## Authentication

```text
POST /signup
POST /login
GET /profile
```

---

## Food Management

```text
POST /food/add
GET /food/today
DELETE /food/delete
```

---

## Weight Tracking

```text
POST /weight/add
GET /weight/history
```

---

## Analytics

```text
GET /analytics/weekly
GET /analytics/monthly
GET /analytics/insights
```

---

## Streaks

```text
GET /streak
```

---

# UI/UX Design Goals

## Design Style
- Modern health-tech interface
- Responsive layout
- Smooth animations
- Clean dashboards
- Glassmorphism cards
- Interactive charts

## Theme
- Dark Blue
- Cyan Highlights
- White Cards
- Light Gray Background

---

# Phase 1 Development Roadmap

## Step 1
Project Setup
- React setup
- Flask setup
- MongoDB connection
- Tailwind setup

---

## Step 2
Authentication System
- Signup
- Login
- JWT authentication

---

## Step 3
Calorie Calculations
- BMR
- TDEE
- Daily targets

---

## Step 4
Dashboard Development
- Summary cards
- Food logging
- Progress ring

---

## Step 5
Daily Log System
- Save food entries
- Calculate deficits

---

## Step 6
Analytics Development
- Graphs
- Reports
- Trends

---

## Step 7
Streak System
- Heatmap calendar
- Streak tracking

---

## Step 8
Weight Tracking
- Weight logs
- Goal prediction

---

## Step 9
Smart Insights Engine
- Weekly analysis
- Consistency tracking

---

## Step 10
Gamification
- Achievement badges
- Habit tracker

---

# Future Scope (Phase 2+)

- AI Food Recognition
- Barcode Scanner
- Nutrition API Integration
- Workout Tracking
- AI Recommendations
- Mobile App
- Social Challenges
- Voice Logging

---

# Final Goal

The objective of GetFitX is to create a modern calorie tracking ecosystem that helps users:

- Track calories effectively
- Maintain calorie deficits
- Visualize long-term progress
- Build healthy habits
- Stay consistent through streaks and gamification

This project is being developed phase-by-phase with scalability and future AI integration in mind.