'use client'

import { useState, useEffect } from 'react'
import { BarChart3, TrendingUp, ShoppingCart, Clock } from 'lucide-react'

export default function DashboardPage() {
  const [stats, setStats] = useState({
    total_revenue: 0,
    total_orders: 0,
    average_order_value: 0,
    active_orders: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch dashboard stats
    const orgId = localStorage.getItem('org_id') || ''
    fetch(`/api/admin/dashboard?organization_id=${orgId}`)
      .then(r => r.json())
      .then(data => setStats(data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const StatCard = ({ icon: Icon, label, value, trend }: any) => (
    <div className="card p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-amber-600 font-medium">{label}</p>
          <p className="text-2xl font-bold text-amber-900 mt-2">{value}</p>
          {trend && <p className="text-xs text-green-600 mt-1">↑ {trend}</p>}
        </div>
        <div className="bg-gradient-to-br from-amber-100 to-orange-100 p-3 rounded-lg">
          <Icon className="w-6 h-6 text-orange-600" />
        </div>
      </div>
    </div>
  )

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-amber-900">Dashboard</h1>
        <p className="text-amber-600 mt-2">Welcome back! Here's your café overview.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={TrendingUp}
          label="Total Revenue"
          value={`₽${(stats.total_revenue / 100).toFixed(2)}`}
          trend="12% vs last month"
        />
        <StatCard
          icon={ShoppingCart}
          label="Total Orders"
          value={stats.total_orders}
          trend="8% vs last month"
        />
        <StatCard
          icon={BarChart3}
          label="Average Order Value"
          value={`₽${(stats.average_order_value / 100).toFixed(2)}`}
        />
        <StatCard
          icon={Clock}
          label="Active Orders"
          value={stats.active_orders}
          trend="Real-time"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card p-6">
          <h2 className="text-lg font-bold text-amber-900 mb-4">Recent Orders</h2>
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="flex items-center justify-between p-4 bg-amber-50 rounded-lg">
                <div>
                  <p className="font-medium text-amber-900">Order #{String(i).padStart(6, '0')}</p>
                  <p className="text-sm text-amber-600">2 items • Takeaway</p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-amber-900">₽550.00</p>
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Ready</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-bold text-amber-900 mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <button className="btn-primary w-full">New Order</button>
            <button className="btn-secondary w-full">View Menu</button>
            <button className="btn-secondary w-full">Staff Management</button>
          </div>
        </div>
      </div>
    </div>
  )
}
