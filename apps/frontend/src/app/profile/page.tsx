'use client';

import React, { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { apiRequest } from '@/lib/api';

export default function ProfilePage() {
  const { user, logout, updateUser, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    current_city: '',
    current_state: '',
    experience_level: ''
  });

  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || '',
        phone: (user as any).phone || '',
        current_city: (user as any).current_city || '',
        current_state: (user as any).current_state || '',
        experience_level: (user as any).experience_level || ''
      });
    }
  }, [user]);

  if (isLoading) return <div className="p-12 text-center animate-pulse">Loading...</div>;

  if (!isAuthenticated) {
    router.push('/login');
    return null;
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const updatedUser = await apiRequest('/users/me', {
        method: 'PUT',
        body: JSON.stringify(formData),
      });
      updateUser(updatedUser);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update profile:', error);
      alert('Failed to save profile changes.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
      <div className="md:flex md:items-center md:justify-between mb-8">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            My Profile
          </h2>
        </div>
        <div className="mt-4 flex md:mt-0 md:ml-4">
          {!isEditing ? (
            <Button onClick={() => setIsEditing(true)}>
              Edit Profile
            </Button>
          ) : (
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setIsEditing(false)} disabled={isSaving}>
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={isSaving}>
                {isSaving ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          )}
        </div>
      </div>
      
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-8 sm:p-10">
          <div className="flex items-center gap-6 mb-8 pb-8 border-b border-gray-200">
            {user?.profile_image ? (
              <img src={user.profile_image} alt={user.name || ''} className="w-24 h-24 rounded-full border border-gray-200 shadow-sm" />
            ) : (
              <div className="w-24 h-24 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-3xl font-bold shadow-sm">
                {user?.name?.substring(0, 1) || user?.email.substring(0, 1).toUpperCase()}
              </div>
            )}
            <div className="flex-1">
              {!isEditing ? (
                <>
                  <h2 className="text-2xl font-bold text-gray-900">{user?.name}</h2>
                  <p className="text-gray-500 font-medium">{user?.email}</p>
                </>
              ) : (
                <div className="max-w-xs space-y-2">
                  <Label htmlFor="name">Full Name</Label>
                  <Input id="name" name="name" value={formData.name} onChange={handleChange} />
                </div>
              )}
              
              {!isEditing && (
                <div className="mt-2 flex gap-2">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Active
                  </span>
                  {(user as any)?.experience_level && (
                     <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                       {(user as any).experience_level}
                     </span>
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8 pb-8 border-b border-gray-200">
            <div>
              <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">Contact Information</h3>
              <dl className="space-y-4">
                <div>
                  <dt className="text-sm text-gray-500 mb-1">Phone</dt>
                  {!isEditing ? (
                    <dd className="text-sm font-medium text-gray-900">{(user as any)?.phone || 'Not provided'}</dd>
                  ) : (
                    <Input id="phone" name="phone" value={formData.phone} onChange={handleChange} placeholder="Not provided" />
                  )}
                </div>
                <div>
                  <dt className="text-sm text-gray-500 mb-1">City</dt>
                  {!isEditing ? (
                    <dd className="text-sm font-medium text-gray-900">{(user as any)?.current_city || 'Not provided'}</dd>
                  ) : (
                    <Input id="current_city" name="current_city" value={formData.current_city} onChange={handleChange} placeholder="Not provided" />
                  )}
                </div>
                <div>
                  <dt className="text-sm text-gray-500 mb-1">State</dt>
                  {!isEditing ? (
                    <dd className="text-sm font-medium text-gray-900">{(user as any)?.current_state || 'Not provided'}</dd>
                  ) : (
                    <Input id="current_state" name="current_state" value={formData.current_state} onChange={handleChange} placeholder="Not provided" />
                  )}
                </div>
              </dl>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">Account Details</h3>
              <dl className="space-y-4">
                <div>
                  <dt className="text-sm text-gray-500 mb-1">Experience Level</dt>
                  {!isEditing ? (
                    <dd className="text-sm font-medium text-gray-900">{(user as any)?.experience_level || 'Not provided'}</dd>
                  ) : (
                    <select
                      id="experience_level"
                      name="experience_level"
                      value={formData.experience_level}
                      onChange={handleChange}
                      className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                    >
                      <option value="" disabled>Select level</option>
                      <option value="Fresher">Fresher</option>
                      <option value="Internship">Internship</option>
                      <option value="0-1 years">0-1 years</option>
                      <option value="1-3 years">1-3 years</option>
                      <option value="3-5 years">3-5 years</option>
                      <option value="5+ years">5+ years</option>
                    </select>
                  )}
                </div>
                <div>
                  <dt className="text-sm text-gray-500 mb-1">Role</dt>
                  <dd className="text-sm font-medium text-gray-900">{(user as any)?.role || 'User'}</dd>
                </div>
              </dl>
            </div>
          </div>

          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-gray-900">Job Preferences</h3>
                <p className="text-sm text-gray-500">Update your preferences for personalized recommendations.</p>
              </div>
              <Button onClick={() => router.push('/profile/preferences')}>
                Edit Preferences
              </Button>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-gray-900">Resume</h3>
                <p className="text-sm text-gray-500">Upload your resume to instantly build your profile.</p>
              </div>
              <Button variant="outline" onClick={() => router.push('/profile/resume')}>
                Manage Resume
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
