'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { apiRequest } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function OnboardingPage() {
  const router = useRouter();
  const { user, updateUser, isAuthenticated, isLoading } = useAuth();
  
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    current_city: '',
    current_state: '',
    experience_level: '',
    education: '', // Not strictly in User schema, but we can add or ignore for now
  });

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
    if (!isLoading && isAuthenticated && user?.onboarding_completed) {
      router.push('/jobs');
    }
    
    if (user) {
      setFormData(prev => ({
        ...prev,
        name: user.name || '',
        email: user.email || '',
        phone: (user as any).phone || '',
        current_city: (user as any).current_city || '',
        current_state: (user as any).current_state || '',
        experience_level: (user as any).experience_level || '',
      }));
    }
  }, [isLoading, isAuthenticated, user, router]);

  if (isLoading || !isAuthenticated) return null;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleComplete = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setError('');
    
    try {
      // 1. Update User basic information
      await apiRequest('/users/me', {
        method: 'PUT',
        body: JSON.stringify({
          name: formData.name,
          phone: formData.phone,
          current_city: formData.current_city,
          current_state: formData.current_state,
          experience_level: formData.experience_level,
        }),
      });
      
      // 2. Mark onboarding as complete (if there's a specific endpoint, or just through /users/me if supported, 
      // but usually the backend will handle this or we can just consider them onboarded locally for now)
      updateUser({ 
        name: formData.name,
        onboarding_completed: true, 
      });
      
      router.push('/jobs');
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to save profile information');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Complete Your Profile
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Just a few basic details to get you started.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-xl">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <form className="space-y-6" onSubmit={handleComplete}>
            
            {error && (
              <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-1">
                <Label htmlFor="name">Full Name</Label>
                <Input
                  id="name"
                  name="name"
                  type="text"
                  required
                  value={formData.name}
                  onChange={handleChange}
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="email">Email address</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  disabled
                  value={formData.email}
                  className="bg-gray-100 cursor-not-allowed text-gray-500"
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="phone">Mobile Number</Label>
                <Input
                  id="phone"
                  name="phone"
                  type="tel"
                  required
                  value={formData.phone}
                  onChange={handleChange}
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="experience_level">Experience Level</Label>
                <select
                  id="experience_level"
                  name="experience_level"
                  required
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
              </div>

              <div className="space-y-1">
                <Label htmlFor="current_city">Current City</Label>
                <Input
                  id="current_city"
                  name="current_city"
                  type="text"
                  required
                  value={formData.current_city}
                  onChange={handleChange}
                />
              </div>

              <div className="space-y-1">
                <Label htmlFor="current_state">Current State</Label>
                <Input
                  id="current_state"
                  name="current_state"
                  type="text"
                  required
                  value={formData.current_state}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="pt-4">
              <Button type="submit" className="w-full text-lg py-6" disabled={isSaving}>
                {isSaving ? 'Saving...' : 'Continue to Jobs'}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
