'use client'

import { Bell, User, Settings } from 'lucide-react'

export default function Header() {
  return (
    <div className="bg-white border-b border-amber-100 px-8 py-4 flex items-center justify-between">
      <div>
        <p className="text-amber-600 text-sm">MONO COFFEE • Main Branch</p>
      </div>
      <div className="flex items-center space-x-6">
        <button className="relative p-2 hover:bg-amber-50 rounded-lg transition">
          <Bell className="w-5 h-5 text-amber-900" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>
        <button className="p-2 hover:bg-amber-50 rounded-lg transition">
          <Settings className="w-5 h-5 text-amber-900" />
        </button>
        <div className="w-10 h-10 bg-gradient-to-br from-amber-400 to-orange-500 rounded-full flex items-center justify-center">
          <User className="w-5 h-5 text-white" />
        </div>
      </div>
    </div>
  )
}
