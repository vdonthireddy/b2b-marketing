import { User } from "lucide-react";

interface ActiveUsersProps {
  users: Array<{ id: string; name: string }>;
}

export function ActiveUsers({ users }: ActiveUsersProps) {
  if (!users || users.length === 0) return null;

  return (
    <div className="flex items-center">
      <div className="flex -space-x-2 mr-2">
        {users.slice(0, 3).map((u, i) => (
          <div 
            key={u.id} 
            className="w-8 h-8 rounded-full bg-primary/20 border-2 border-background flex items-center justify-center relative"
            title={u.name}
            style={{ zIndex: 10 - i }}
          >
            <span className="text-xs font-bold text-primary">{u.name.substring(0, 1).toUpperCase()}</span>
          </div>
        ))}
        {users.length > 3 && (
          <div className="w-8 h-8 rounded-full bg-secondary border-2 border-background flex items-center justify-center relative z-0">
            <span className="text-xs font-bold text-gray-400">+{users.length - 3}</span>
          </div>
        )}
      </div>
      <span className="text-xs text-gray-400 font-medium">
        {users.length} online
      </span>
    </div>
  );
}
