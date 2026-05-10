"""
Tests for memory and learning system

Tests:
- Task storage and retrieval
- Embedding and similarity search
- Pattern learning and application
- Memory statistics
"""

import pytest
from src.memory.agent_db import AgentDB
from src.memory.task_embedder import TaskEmbedder
from src.memory.sona_learner import SONALearner


class TestAgentDB:
    """Tests for AgentDB"""
    
    def test_store_task(self):
        """Test storing task"""
        db = AgentDB()
        
        task_data = {
            'description': 'Create email validator',
            'code': 'function validate(email) { ... }',
            'success': True
        }
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        result = db.store_task('task_1', task_data, embedding)
        assert result is True
    
    def test_retrieve_task(self):
        """Test retrieving task"""
        db = AgentDB()
        
        task_data = {
            'description': 'Create email validator',
            'code': 'function validate(email) { ... }',
            'success': True
        }
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        db.store_task('task_1', task_data, embedding)
        retrieved = db.retrieve_task('task_1')
        
        assert retrieved is not None
        assert retrieved['description'] == 'Create email validator'
    
    def test_search_similar(self):
        """Test similarity search"""
        db = AgentDB()
        
        # Store multiple tasks
        tasks = [
            {'description': 'Create email validator', 'success': True},
            {'description': 'Create password validator', 'success': True},
            {'description': 'Create URL validator', 'success': True},
        ]
        
        for i, task in enumerate(tasks):
            embedding = [0.1 * (i+1), 0.2 * (i+1), 0.3 * (i+1)]
            db.store_task(f'task_{i}', task, embedding)
        
        # Search for similar
        query_embedding = [0.1, 0.2, 0.3]
        results = db.search_similar(query_embedding, top_k=2)
        
        assert len(results) <= 2
        assert all('similarity_score' in r for r in results)
    
    def test_get_stats(self):
        """Test getting database statistics"""
        db = AgentDB()
        
        # Store tasks
        for i in range(3):
            task_data = {'description': f'Task {i}', 'success': i % 2 == 0}
            embedding = [0.1 * (i+1)] * 5
            db.store_task(f'task_{i}', task_data, embedding)
        
        stats = db.get_stats()
        
        assert stats['total_tasks'] == 3
        assert stats['successful_tasks'] >= 0
        assert 0 <= stats['average_success_rate'] <= 1


class TestTaskEmbedder:
    """Tests for TaskEmbedder"""
    
    def test_build_vocabulary(self):
        """Test building vocabulary"""
        embedder = TaskEmbedder()
        
        documents = [
            'Create email validator function',
            'Create password validator function',
            'Create URL validator function'
        ]
        
        embedder.build_vocabulary(documents)
        
        assert embedder.vocab_size > 0
        assert len(embedder.vocabulary) > 0
    
    def test_embed_task(self):
        """Test embedding task"""
        embedder = TaskEmbedder()
        
        documents = [
            'Create email validator',
            'Create password validator',
            'Create URL validator'
        ]
        embedder.build_vocabulary(documents)
        
        embedding = embedder.embed_task('Create email validator')
        
        assert len(embedding) == embedder.vocab_size
        assert all(isinstance(x, float) for x in embedding)
    
    def test_embed_without_vocabulary(self):
        """Test embedding without building vocabulary"""
        embedder = TaskEmbedder()
        
        embedding = embedder.embed_task('Create email validator')
        
        assert len(embedding) == 100  # Default size
        assert all(isinstance(x, float) for x in embedding)
    
    def test_embedding_similarity(self):
        """Test that similar tasks have similar embeddings"""
        embedder = TaskEmbedder()
        
        documents = [
            'Create email validator',
            'Create password validator',
            'Create URL validator'
        ]
        embedder.build_vocabulary(documents)
        
        emb1 = embedder.embed_task('Create email validator')
        emb2 = embedder.embed_task('Create email validator')
        
        # Same task should have identical embedding
        assert emb1 == emb2


class TestSONALearner:
    """Tests for SONA Learner"""
    
    def test_learn_from_task(self):
        """Test learning from task"""
        learner = SONALearner()
        
        task = {
            'id': 'task_1',
            'type': 'validation',
            'description': 'Create email validator'
        }
        
        result = {
            'success': True,
            'solution_type': 'regex',
            'code_pattern': 'function validate(email) { ... }',
            'execution_time': 2.5
        }
        
        learned = learner.learn_from_task(task, result)
        assert learned is True
    
    def test_get_applicable_patterns(self):
        """Test getting applicable patterns"""
        learner = SONALearner()
        
        # Learn from tasks
        tasks = [
            {
                'id': 'task_1',
                'type': 'validation',
                'description': 'Create email validator'
            },
            {
                'id': 'task_2',
                'type': 'validation',
                'description': 'Create password validator'
            }
        ]
        
        for task in tasks:
            result = {'success': True, 'solution_type': 'regex'}
            learner.learn_from_task(task, result)
        
        # Get applicable patterns
        new_task = {
            'type': 'validation',
            'description': 'Create URL validator'
        }
        
        patterns = learner.get_applicable_patterns(new_task, top_k=2)
        
        assert len(patterns) <= 2
        assert all('success_rate' in p for p in patterns)
    
    def test_get_stats(self):
        """Test getting learning statistics"""
        learner = SONALearner()
        
        # Learn from tasks
        for i in range(3):
            task = {
                'id': f'task_{i}',
                'type': 'validation',
                'description': f'Create validator {i}'
            }
            result = {'success': i % 2 == 0}
            learner.learn_from_task(task, result)
        
        stats = learner.get_stats()
        
        assert stats['total_patterns'] > 0
        assert stats['total_executions'] == 3
        assert 0 <= stats['average_success_rate'] <= 1


class TestMemoryIntegration:
    """Integration tests for memory system"""
    
    def test_full_memory_workflow(self):
        """Test full memory workflow"""
        db = AgentDB()
        embedder = TaskEmbedder()
        learner = SONALearner()
        
        # Build vocabulary
        documents = [
            'Create email validator',
            'Create password validator',
            'Create URL validator'
        ]
        embedder.build_vocabulary(documents)
        
        # Store tasks with embeddings
        for i, doc in enumerate(documents):
            task_data = {
                'description': doc,
                'code': f'function validate_{i}() {{ ... }}',
                'success': True
            }
            embedding = embedder.embed_task(doc)
            db.store_task(f'task_{i}', task_data, embedding)
            
            # Learn from task
            result = {'success': True, 'solution_type': 'regex'}
            learner.learn_from_task(task_data, result)
        
        # Search for similar
        query = 'Create email validator'
        query_embedding = embedder.embed_task(query)
        similar_tasks = db.search_similar(query_embedding, top_k=2)
        
        assert len(similar_tasks) > 0
        
        # Get applicable patterns
        new_task = {'description': 'Create email validator'}
        patterns = learner.get_applicable_patterns(new_task)
        
        assert len(patterns) > 0
        
        # Check stats
        db_stats = db.get_stats()
        learner_stats = learner.get_stats()
        
        assert db_stats['total_tasks'] == 3
        assert learner_stats['total_patterns'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
