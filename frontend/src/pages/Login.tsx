import React from 'react'

export default function Login() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="bg-card p-8 rounded-lg shadow-lg w-full max-w-md">
        <h1 className="text-2xl font-bold mb-4 text-center">Login</h1>
        <form className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input 
              type="email" 
              className="w-full px-3 py-2 border border-border rounded-lg"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Password</label>
            <input 
              type="password" 
              className="w-full px-3 py-2 border border-border rounded-lg"
              placeholder="••••••••"
            />
          </div>
          <button 
            type="submit"
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground py-2 rounded-lg"
          >
            Sign In
          </button>
        </form>
      </div>
    </div>
  )
}