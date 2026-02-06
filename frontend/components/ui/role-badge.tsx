interface RoleBadgeProps {
  role: 'admin' | 'manager' | 'rep';
}

export function RoleBadge({ role }: RoleBadgeProps) {
  const colors = {
    admin: 'bg-red-100 text-red-800',
    manager: 'bg-blue-100 text-blue-800',
    rep: 'bg-gray-100 text-gray-800'
  };

  return (
    <span className={`px-2 py-1 text-xs rounded ${colors[role]}`}>
      {role}
    </span>
  );
}
