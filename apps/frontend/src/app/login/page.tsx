'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '@/context/AuthContext';
import { apiRequest, API_BASE_URL } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Compass } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // OAuth2 requires form data (x-www-form-urlencoded) for token endpoint
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
      });

      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      // After getting token, we need to fetch user profile since login doesn't return user object
      const userRes = await fetch(`${API_BASE_URL}/users/me`, {
        headers: {
          'Authorization': `Bearer ${data.access_token}`
        }
      });
      
      const userData = await userRes.json();
      
      if (!userRes.ok) {
        throw new Error(userData.detail || 'Failed to fetch user profile');
      }

      login(data.access_token, userData);
      router.push('/jobs');
    } catch (err: any) {
      setError(err.message || 'Invalid email or password');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse: any) => {
    setIsLoading(true);
    setError('');
    
    try {
      const data = await apiRequest('/auth/google', {
        method: 'POST',
        body: JSON.stringify({ token: credentialResponse.credential }),
      });
      
      login(data.access_token, data.user);
      router.push('/jobs');
    } catch (err: any) {
      setError(err.message || 'Failed to authenticate with Google');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)] bg-[#FDFBF7] items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Decorative background blobs */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-orange-100 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob"></div>
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-yellow-100 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob animation-delay-2000"></div>

      <div className="w-full max-w-md bg-white/80 backdrop-blur-xl p-10 rounded-3xl shadow-xl border border-white/50 relative z-10">
        <div className="mx-auto w-full">
          <div className="text-center mb-8">
            <Link href="/" className="inline-flex items-center gap-2 text-orange-600 mb-6">
              <div className="w-12 h-12 bg-orange-50 rounded-2xl flex items-center justify-center border border-orange-100">
                <Compass className="h-7 w-7" />
              </div>
            </Link>
            <h2 className="text-3xl font-extrabold tracking-tight text-gray-900">
              Welcome back
            </h2>
            <p className="mt-3 text-sm text-gray-500 font-medium">
              Don't have an account?{' '}
              <Link href="/register" className="text-orange-600 hover:text-orange-700 font-bold transition-colors">
                Sign up for free
              </Link>
            </p>
          </div>

          <div className="mt-8">
            <div className="mt-6">
              <form onSubmit={handleEmailLogin} className="space-y-6">
                {error && (
                  <div className="bg-red-50 border-l-4 border-red-400 p-4">
                    <div className="flex">
                      <div className="ml-3">
                        <p className="text-sm text-red-700">{error}</p>
                      </div>
                    </div>
                  </div>
                )}
                
                <div className="space-y-2">
                  <Label htmlFor="email" className="font-semibold text-gray-700">Email address</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={isLoading}
                    className="rounded-xl bg-gray-50 border-gray-200 focus:bg-white transition-colors"
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="password" className="font-semibold text-gray-700">Password</Label>
                    <div className="text-sm">
                      <a href="#" className="font-medium text-orange-600 hover:text-orange-700 transition-colors">
                        Forgot your password?
                      </a>
                    </div>
                  </div>
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={isLoading}
                    className="rounded-xl bg-gray-50 border-gray-200 focus:bg-white transition-colors"
                  />
                </div>

                <div className="pt-2">
                  <Button type="submit" className="w-full bg-orange-600 hover:bg-orange-700 text-white font-bold py-6 rounded-xl shadow-md transition-all text-base" disabled={isLoading}>
                    {isLoading ? 'Signing in...' : 'Sign in to Career Maps'}
                  </Button>
                </div>
              </form>
              
              <div className="mt-6">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white text-gray-500">Or continue with</span>
                  </div>
                </div>

                <div className="mt-6 flex justify-center">
                  <GoogleLogin
                    onSuccess={handleGoogleSuccess}
                    onError={() => setError('Google Login Failed')}
                    theme="outline"
                    width="384"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
