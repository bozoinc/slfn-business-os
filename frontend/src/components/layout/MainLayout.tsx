import React from 'react'
import { Outlet } from 'react-router-dom'

export default function MainLayout() {
  return (
    <div className="min-h-screen bg-background">
      <nav className="bg-card border-b border-border p-4">
        <div className="container mx-auto flex space-x-4">
          <a href="/" className="text-foreground hover:text-primary">Dashboard</a>
          <a href="/contacts" className="text-foreground hover:text-primary">Contacts</a>
          <a href="/deals" className="text-foreground hover:text-primary">Deals</a>
          <a href="/forms" className="text-foreground hover:text-primary">Forms</a>
          <a href="/settings" className="text-foreground hover:text-primary">Settings</a>
        </div>
      </nav>
      <main className="container mx-auto p-4">
        <Outlet />
      </main>
    </div>
  )
}