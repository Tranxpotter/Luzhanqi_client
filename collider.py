from abc import ABC, abstractmethod
import pygame
import warnings

class Collider(ABC):
    @abstractmethod
    def on_collide(self, obj) -> None:...
    
    @abstractmethod
    def post_collide(self) -> bool:
        '''Return the decision to remove the object from collider manager'''
    
    @abstractmethod
    def post_check_collisions(self) -> None:...

class ColliderManager:
    def __init__(self) -> None:
        self.objects:list[Collider] = []
    
    def add(self, obj:Collider):
        self.objects.append(obj)
    
    def remove(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)
    
    def check_collision(self):
        ignores = []
        for index, object1 in enumerate(self.objects):
            if object1 in ignores:
                continue
            for object2 in self.objects[index+1:]:
                if object2 in ignores:
                    continue
                try:
                    rect1:pygame.Rect = object1.__getattribute__("rect")
                    rect2:pygame.Rect = object2.__getattribute__("rect")
                except AttributeError:
                    warnings.warn(f"One or more colliders missing attribute [rect] from collision of {object1}<->{object2}")
                    return
                
                if rect1.colliderect(rect2):
                    object1.on_collide(object2)
                    object2.on_collide(object1)
                    to_remove = object1.post_collide()
                    if to_remove:
                        ignores.append(object1)
                    to_remove = object2.post_collide()
                    if to_remove:
                        ignores.append(object2)

        for ignore in ignores:
            self.objects.remove(ignore)
        
        for object in self.objects:
            object.post_check_collisions()
    
    