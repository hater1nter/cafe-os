'use client'

import { Coffee, Package, Users, Settings, LogOut, Menu } from 'lucide-react'
import Link from 'next/link'
import { useState } from 'react'

export default function Sidebar() {
  const [open, setOpen] = useState(true)

  const items = [
    { icon: BarChart3, label: 'Dashboard', href: '/dashboard' },
    { icon: ShoppingCart, label: 'Orders', href: '/dashboard/orders' },
    { icon: Package, label: 'Menu', href: '/dashboard/menu' },
    { icon: Users, label: 'Staff', href: '/dashboard/staff' },
    { icon: Settings, label: 'Settings', href: '/dashboard/settings' },
  ]

  return (
    <div className={`${open ? 'w-64' : 'w-20'} bg-white border-r border-amber-100 transition-all duration-300 flex flex-col`}>
      {/* Logo */}
      <div className="p-4 border-b border-amber-100 flex items-center justify-between">
        {open && <h1 className="font-bold text-amber-900">Café OS</h1>}
        <button
          onClick={() => setOpen(!open)}
          className="p-2 hover:bg-amber-50 rounded"
        >
          <Menu className="w-4 h-4" />
        </button>
      </div>

      {/* Nav Items */}
      <nav className="flex-1 p-4 space-y-2">
        {items.map(item => (
          <Link
            key={item.href}
            href={item.href}
            className="flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-amber-50 text-amber-900 transition"
          >
            <item.icon className="w-5 h-5" />
            {open && <span className="text-sm font-medium">{item.label}</span>}
          </Link>
        ))}
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-amber-100">
        <button className="flex items-center space-x-3 w-full px-4 py-3 rounded-lg hover:bg-red-50 text-red-600 transition">
          <LogOut className="w-5 h-5" />
          {open && <span className="text-sm font-medium">Logout</span>}
        </button>
      </div>
    </div>
  )
}

import { BarChart3, ShoppingCart } from 'lucide-react'
